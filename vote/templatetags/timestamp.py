from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def comment_time(value):
    if not value:
        return ""

    # timzone aware
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())

    
    delta = timezone.now() - value

    if delta < timedelta(minutes=1):
        seconds = int(delta.total_seconds())
        return "Just now" if seconds < 5 else f"{seconds} seconds ago"
    elif delta < timedelta(hours=1):
        minutes = int(delta.total_seconds() // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif delta < timedelta(days=1):
        hours = int(delta.total_seconds() // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif delta < timedelta(days=5):
        days = delta.days
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return f"{value.strftime('%B')} {value.day}, {value.year}"
