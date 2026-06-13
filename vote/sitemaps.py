from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Video


class VideoSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Video.objects.filter(is_active=True, needs_review=False).order_by("-date")

    def lastmod(self, obj):
        return obj.date

    def location(self, obj):
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return ["index", "browse", "about", "rules", "guide", "video_form"]

    def location(self, item):
        return reverse(item)
