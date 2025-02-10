from django.contrib import admin
from .models import Video, Result, YoutubeQuota, VoteUser
# Register your models here.


admin.site.register(Video)
admin.site.register(Result)
admin.site.register(YoutubeQuota)
admin.site.register(VoteUser)
