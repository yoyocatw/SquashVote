from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


@shared_task
def fetch_replies():
    logger.info("Running fetch replies command through Celery...")
    call_command("fetch_replies")
    return "fetch replies ran succesfully"

@shared_task
def post_comment():
    logger.info("Running post comment command through Celery...")
    call_command("post_comment")
    return "post comment ran succesfully"
