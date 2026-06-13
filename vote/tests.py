"""
Test suite for the vote app.

Covers the model invariants (Result auto-creation, timestamp parsing, the
duplicate-vote constraint) and the view behaviour that the redesign depends on:
vote counting, percentage math, browse filters/pagination, the next-decision
and suggested-videos queries, the comment actions, and a smoke pass that every
route renders.

Run with:  python manage.py test
"""

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta

from .models import Video, Result, VoteUser, Comment, CommentLike, CommentReport
from .forms import VoteForm, extract_video_id


def make_video(**kwargs):
    """Create an active, review-passed Video (Result is auto-created via signal)."""
    defaults = dict(
        video_title="Test Clip",
        timestamp="1:30",
        video_id="abc123",
        org_decision=Video.Decision.STROKE,
        category=Video.Category.PSA,
        is_active=True,
        needs_review=False,
    )
    defaults.update(kwargs)
    return Video.objects.create(**defaults)


def clip_url(video):
    return reverse("video_result", args=[video.id, slugify(video.video_title)])


def make_comment(video, **kwargs):
    """Create a Comment the way the views do (anonymous = user=None).

    Note: Comment.user / CommentReport.user carry a buggy ``default="Anonymous"``
    (a string where a User id is expected). The app never triggers it because
    every view passes ``user`` explicitly; tests must do the same.
    """
    kwargs.setdefault("user", None)
    kwargs.setdefault("comment", "comment body")
    return Comment.objects.create(video=video, **kwargs)


# --------------------------------------------------------------------------- #
# Models
# --------------------------------------------------------------------------- #
class ModelTests(TestCase):
    def test_result_auto_created_on_video_save(self):
        video = make_video()
        self.assertTrue(Result.objects.filter(video=video).exists())
        self.assertEqual(video.result.total_votes, 0)

    def test_convert_timestamp_to_seconds(self):
        self.assertEqual(Video.convert_timestamp_to_seconds("1:30"), 90)
        self.assertEqual(Video.convert_timestamp_to_seconds("1:06:09"), 3969)
        self.assertEqual(Video.convert_timestamp_to_seconds("garbage"), 0)

    def test_start_property(self):
        self.assertEqual(make_video(timestamp="2:00").start, 120)

    def test_duplicate_vote_constraint_at_db_level(self):
        video = make_video()
        VoteUser.objects.create(video=video, session_id="sess-1", vote="stroke")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                VoteUser.objects.create(video=video, session_id="sess-1", vote="let")


# --------------------------------------------------------------------------- #
# Forms
# --------------------------------------------------------------------------- #
class FormTests(TestCase):
    def test_extract_video_id_watch_url(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/watch?v=WE0fSTz7LB0"),
            "WE0fSTz7LB0",
        )

    def test_extract_video_id_short_url(self):
        self.assertEqual(extract_video_id("https://youtu.be/WE0fSTz7LB0"), "WE0fSTz7LB0")

    def test_extract_video_id_invalid(self):
        self.assertIsNone(extract_video_id("https://example.com/not-a-video"))

    def test_vote_form_rejects_unknown_choice(self):
        self.assertFalse(VoteForm({"vote": "maybe"}).is_valid())
        self.assertTrue(VoteForm({"vote": "stroke"}).is_valid())


# --------------------------------------------------------------------------- #
# Voting flow
# --------------------------------------------------------------------------- #
class VoteFlowTests(TestCase):
    def setUp(self):
        self.video = make_video()
        self.url = clip_url(self.video)

    def test_pre_vote_shows_form_not_results(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.context["already_voted"])
        self.assertContains(r, 'name="vote"')
        # suggestions are gated behind voting
        self.assertNotContains(r, 'id="videos"')

    def test_vote_creates_record_and_increments_result(self):
        r = self.client.post(self.url, {"vote": "stroke"})
        self.assertEqual(r.status_code, 200)
        self.video.result.refresh_from_db()
        self.assertEqual(self.video.result.total_votes, 1)
        self.assertEqual(self.video.result.stroke, 1)
        self.assertEqual(self.video.result.let, 0)
        self.assertEqual(VoteUser.objects.filter(video=self.video).count(), 1)

    def test_duplicate_vote_does_not_double_count(self):
        self.client.post(self.url, {"vote": "stroke"})
        # same client = same session; a second vote must be ignored
        self.client.post(self.url, {"vote": "let"})
        self.video.result.refresh_from_db()
        self.assertEqual(self.video.result.total_votes, 1)
        self.assertEqual(self.video.result.stroke, 1)
        self.assertEqual(self.video.result.let, 0)
        self.assertEqual(VoteUser.objects.filter(video=self.video).count(), 1)

    def test_after_voting_results_and_suggestions_show(self):
        other = make_video(video_id="other1", video_title="Other Clip")
        self.client.post(self.url, {"vote": "stroke"})
        r = self.client.get(self.url)
        self.assertTrue(r.context["already_voted"])
        self.assertContains(r, 'id="videos"')          # suggestions section rendered
        self.assertContains(r, other.video_title)

    def test_percentages_rounded(self):
        self.video.result.total_votes = 4
        self.video.result.stroke = 2
        self.video.result.let = 1
        self.video.result.no_let = 1
        self.video.result.save()
        r = self.client.get(self.url)
        self.assertEqual(r.context["stroke_pct"], 50)
        self.assertEqual(r.context["let_pct"], 25)
        self.assertEqual(r.context["nolet_pct"], 25)

    def test_percentages_zero_votes_no_division_error(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context["stroke_pct"], 0)
        self.assertEqual(r.context["let_pct"], 0)
        self.assertEqual(r.context["nolet_pct"], 0)


# --------------------------------------------------------------------------- #
# Browse page
# --------------------------------------------------------------------------- #
class BrowseTests(TestCase):
    def setUp(self):
        self.psa = make_video(video_id="psa1", category=Video.Category.PSA, video_title="PSA clip")
        self.amateur = make_video(
            video_id="am1", category=Video.Category.AMATEUR, video_title="Amateur clip"
        )

    def test_browse_renders_with_counts(self):
        r = self.client.get(reverse("browse"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context["total_decisions"], 2)

    def test_filter_psa(self):
        ids = [v.id for v in self.client.get(reverse("browse"), {"category": "psa"}).context["page_obj"]]
        self.assertIn(self.psa.id, ids)
        self.assertNotIn(self.amateur.id, ids)

    def test_filter_amateur(self):
        ids = [v.id for v in self.client.get(reverse("browse"), {"category": "amateur"}).context["page_obj"]]
        self.assertIn(self.amateur.id, ids)
        self.assertNotIn(self.psa.id, ids)

    def test_unvoted_filter_excludes_voted(self):
        self.client.post(clip_url(self.psa), {"vote": "stroke"})  # vote on psa, same session
        ids = [v.id for v in self.client.get(reverse("browse"), {"category": "unvoted"}).context["page_obj"]]
        self.assertNotIn(self.psa.id, ids)
        self.assertIn(self.amateur.id, ids)

    def test_voted_count_tracks_session(self):
        self.client.post(clip_url(self.psa), {"vote": "let"})
        self.assertEqual(self.client.get(reverse("browse")).context["voted_count"], 1)

    def test_htmx_request_returns_partial(self):
        r = self.client.get(reverse("browse"), HTTP_HX_REQUEST="true")
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "vote/partials/browse_list.html")

    def test_pagination_is_15_per_page(self):
        for i in range(20):
            make_video(video_id=f"vid{i}", video_title=f"Clip {i}")
        r = self.client.get(reverse("browse"))
        self.assertEqual(len(r.context["page_obj"]), 15)
        self.assertTrue(r.context["page_obj"].has_next())


# --------------------------------------------------------------------------- #
# Next decision + suggested videos
# --------------------------------------------------------------------------- #
class NextDecisionTests(TestCase):
    def _dated(self, video, days_ago):
        Video.objects.filter(id=video.id).update(date=timezone.now() - timedelta(days=days_ago))

    def test_next_decision_is_newest_unvoted_excluding_current(self):
        current = make_video(video_id="cur", video_title="Current")
        older = make_video(video_id="old", video_title="Older")
        newer = make_video(video_id="new", video_title="Newer")
        self._dated(current, 5)
        self._dated(older, 3)
        self._dated(newer, 1)
        r = self.client.get(clip_url(current))
        self.assertEqual(r.context["next_video"], newer)

    def test_suggested_videos_excludes_current_and_voted(self):
        current = make_video(video_id="cur", video_title="Current")
        voted = make_video(video_id="vtd", video_title="Already Voted")
        fresh = make_video(video_id="frsh", video_title="Fresh")
        self.client.post(clip_url(voted), {"vote": "let"})  # vote on `voted` first
        suggested = list(self.client.get(clip_url(current)).context["suggested_videos"])
        self.assertIn(fresh, suggested)
        self.assertNotIn(current, suggested)
        self.assertNotIn(voted, suggested)

    def test_inactive_and_review_videos_never_suggested(self):
        current = make_video(video_id="cur", video_title="Current")
        inactive = make_video(video_id="ina", video_title="Inactive", is_active=False)
        in_review = make_video(video_id="rev", video_title="In review", needs_review=True)
        suggested = list(self.client.get(clip_url(current)).context["suggested_videos"])
        self.assertNotIn(inactive, suggested)
        self.assertNotIn(in_review, suggested)


# --------------------------------------------------------------------------- #
# Comments / likes / replies / reports
# --------------------------------------------------------------------------- #
class CommentTests(TestCase):
    def setUp(self):
        self.video = make_video()

    def test_post_comment_creates_root_comment(self):
        r = self.client.post(reverse("post_comment", args=[self.video.id]), {"comment": "Clear stroke."})
        self.assertEqual(r.status_code, 200)
        comment = Comment.objects.get(video=self.video)
        self.assertEqual(comment.comment, "Clear stroke.")
        self.assertIsNone(comment.parent)

    def test_like_toggles_on_and_off(self):
        comment = make_comment(self.video, comment="x")
        url = reverse("like_comment", args=[comment.id])
        self.client.post(url)  # like
        self.assertEqual(CommentLike.objects.filter(comment=comment).count(), 1)
        self.client.post(url)  # same session unlikes
        self.assertEqual(CommentLike.objects.filter(comment=comment).count(), 0)

    def test_like_requires_post(self):
        comment = make_comment(self.video, comment="x")
        self.assertEqual(self.client.get(reverse("like_comment", args=[comment.id])).status_code, 405)

    def test_reply_creates_threaded_comment(self):
        parent = make_comment(self.video, comment="parent")
        r = self.client.post(reverse("post_reply", args=[parent.id]), {"reply_content": "child"})
        self.assertEqual(r.status_code, 200)
        reply = Comment.objects.get(parent=parent)
        self.assertEqual(reply.comment, "child")
        self.assertEqual(reply.video, self.video)

    def test_reply_without_content_is_bad_request(self):
        parent = make_comment(self.video, comment="parent")
        self.assertEqual(self.client.post(reverse("post_reply", args=[parent.id]), {}).status_code, 400)

    def test_report_creates_record(self):
        comment = make_comment(self.video, comment="x")
        r = self.client.post(reverse("report", args=[comment.id]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(CommentReport.objects.filter(comment=comment).count(), 1)


# --------------------------------------------------------------------------- #
# Smoke: every page renders
# --------------------------------------------------------------------------- #
class SmokeTests(TestCase):
    def setUp(self):
        self.video = make_video()

    def test_static_routes_return_200(self):
        for name in ["index", "browse", "about", "rules", "guide", "video_form"]:
            with self.subTest(route=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_clip_page_returns_200(self):
        self.assertEqual(self.client.get(clip_url(self.video)).status_code, 200)

    def test_check_duplicate_json(self):
        r = self.client.get(reverse("check_duplicate"), {"video_id": self.video.video_id})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["exists"])


# --------------------------------------------------------------------------- #
# Regression tests for the review fixes
# --------------------------------------------------------------------------- #
class SlugFallbackTests(TestCase):
    def test_symbol_only_title_does_not_break_url_or_pages(self):
        # slugify("!!!") == "" which the <slug:slug> route rejects -> used to 500
        v = make_video(video_id="sym1", video_title="!!! ???")
        self.assertTrue(v.slug)  # falls back to "clip"
        self.assertIn(f"/video/{v.id}/", v.get_absolute_url())
        # pages that loop over all videos must still render
        self.assertEqual(self.client.get(reverse("index")).status_code, 200)
        self.assertEqual(self.client.get(reverse("browse")).status_code, 200)
        self.assertEqual(self.client.get(v.get_absolute_url()).status_code, 200)


class ReportIdempotentTests(TestCase):
    def test_duplicate_report_does_not_500(self):
        video = make_video()
        comment = make_comment(video, comment="x")
        url = reverse("report", args=[comment.id])
        self.assertEqual(self.client.post(url).status_code, 200)
        self.assertEqual(self.client.post(url).status_code, 200)  # repeat must not 500
        self.assertEqual(CommentReport.objects.filter(comment=comment).count(), 1)


class LastClipFallbackTests(TestCase):
    def test_voting_on_only_clip_shows_browse_all(self):
        video = make_video()
        r = self.client.post(clip_url(video), {"vote": "stroke"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Browse all decisions")
        self.assertNotContains(r, "Next One")


class CommentStateTests(TestCase):
    def setUp(self):
        self.video = make_video()

    def test_posting_comment_updates_count_oob(self):
        r = self.client.post(reverse("post_comment", args=[self.video.id]), {"comment": "hi"})
        self.assertContains(r, 'hx-swap-oob="innerHTML:#sv-comment-count"')

    def test_posting_comment_preserves_like_state(self):
        a = make_comment(self.video, comment="first")
        self.client.post(reverse("like_comment", args=[a.id]))  # like A (same session)
        r = self.client.post(reverse("post_comment", args=[self.video.id]), {"comment": "second"})
        # A's like span keeps its liked (white) styling after posting another comment
        self.assertContains(r, f'id="vote-count-{a.id}"')
        self.assertContains(r, "text-white")


class SeoTests(TestCase):
    def setUp(self):
        self.video = make_video()

    def test_sitemap_lists_clip(self):
        r = self.client.get("/sitemap.xml")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, f"/video/{self.video.id}/")

    def test_robots_txt(self):
        r = self.client.get("/robots.txt")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Sitemap:")

    def test_clip_has_canonical_and_jsonld(self):
        html = self.client.get(clip_url(self.video)).content.decode()
        self.assertIn(f'rel="canonical" href="https://squashvote.wtf/video/{self.video.id}/', html)
        self.assertIn('"@type": "VideoObject"', html)
        self.assertIn("og:image", html)

    def test_chart_route_removed(self):
        from django.urls import NoReverseMatch
        with self.assertRaises(NoReverseMatch):
            reverse("chart", args=[self.video.id])
