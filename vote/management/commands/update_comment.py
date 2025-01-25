from django.core.management.base import BaseCommand
from vote.models import Video, Result
from vote.client.youtube_client import youtube_client


class Command(BaseCommand):

    def handle(self, *args, **options):
        youtube = youtube_client()
