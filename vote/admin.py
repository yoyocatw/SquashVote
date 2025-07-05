from django.contrib import admin
from .models import Video, Result, VoteUser, Comment, CommentReport, CommentLike

# Register your models here.
admin.site.site_header = "SquashVote Admin"
admin.site.site_title = "SquashVote Admin Area"
admin.site.index_title = "Welcome to the SquashVote Admin Area"


def delete_reported_comment(modeladmin, request, queryset):
    for report in queryset:
        report.comment.delete()
        report.delete()


delete_reported_comment.short_description = "Delete selected reports and their comments"


class CommentReportAdmin(admin.ModelAdmin):
    list_display = ("comment_text", "user")
    actions = [delete_reported_comment]

    def comment_text(self, obj):
        return obj.comment.comment

    comment_text.short_description = "Reported Comment"


admin.site.register(Video)
admin.site.register(Result)
admin.site.register(VoteUser)
admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(CommentReport, CommentReportAdmin)
