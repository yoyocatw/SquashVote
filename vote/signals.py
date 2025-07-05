from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video, Result


@receiver(post_save, sender=Video)
def create_result(sender, instance, created, **kwargs):
    if created:
        Result.objects.create(video=instance)
