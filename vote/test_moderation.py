"""Access-control tests for the moderation actions (accept/reject video).

Run under Python 3.13 (Django 5.1.5's test client is incompatible with 3.14).
"""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from vote.models import Video


def make_pending_video():
    return Video.objects.create(
        video_title="Pending clip",
        timestamp="0:10",
        video_id="modtest",
        org_decision="Stroke",
        category="PSA",
        is_active=False,
        needs_review=True,
    )


class ModerationAuthTests(TestCase):
    def setUp(self):
        # Use the canonical host so CanonicalUrlMiddleware (unconditional on
        # main) doesn't 301 every request before it reaches the view.
        self.client = Client(SERVER_NAME="squashvote.wtf")
        self.video = make_pending_video()
        self.accept_url = reverse("accept_video", args=[self.video.id])
        self.reject_url = reverse("reject_video", args=[self.video.id])

    def test_anonymous_cannot_reject(self):
        # @login_required redirects to login (302); the clip must survive
        r = self.client.post(self.reject_url)
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Video.objects.filter(id=self.video.id).exists())

    def test_anonymous_cannot_accept(self):
        r = self.client.post(self.accept_url)
        self.assertEqual(r.status_code, 302)
        self.video.refresh_from_db()
        self.assertFalse(self.video.is_active)

    def test_get_is_rejected_even_for_staff(self):
        # @require_POST: a GET (drive-by link / crawler) must not act
        User.objects.create_user("mod", password="pw", is_staff=True)
        self.client.login(username="mod", password="pw")
        self.assertEqual(self.client.get(self.reject_url).status_code, 405)
        self.assertTrue(Video.objects.filter(id=self.video.id).exists())

    def test_staff_can_accept_and_reject_via_post(self):
        User.objects.create_user("mod", password="pw", is_staff=True)
        self.client.login(username="mod", password="pw")

        self.assertEqual(self.client.post(self.accept_url).status_code, 200)
        self.video.refresh_from_db()
        self.assertTrue(self.video.is_active)
        self.assertFalse(self.video.needs_review)

        self.assertEqual(self.client.post(self.reject_url).status_code, 200)
        self.assertFalse(Video.objects.filter(id=self.video.id).exists())
