from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


@shared_task
def fetch_replies():
    logger.info("Running fetch replies command through Celery...")
    call_command("fetch_replies")
    return "fetch replies ran succesfully"
