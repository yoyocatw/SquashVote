from django.contrib import admin
from .models import Video, Result, VoteUser

# Register your models here.
admin.site.site_header = "SquashVote Admin"
admin.site.site_title = "SquashVote Admin Area"
admin.site.index_title = "Welcome to the SquashVote Admin Area"

admin.site.register(Video)
admin.site.register(Result)
admin.site.register(VoteUser)
