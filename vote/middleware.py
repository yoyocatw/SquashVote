from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalUrlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.canonical_domain = getattr(settings, 'CANONICAL_DOMAIN', 'squashvote.wtf')

    def __call__(self, request):
        current_host = request.get_host()
        if current_host.lower() != self.canonical_domain.lower():
            new_url = f"https://{self.canonical_domain}"
            return HttpResponsePermanentRedirect(new_url)
        return self.get_response(request)