from django.contrib import admin
from .models import UserNotification, CommunityNotification, NoticeComment, NoticeStatus

class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'community', 'notification_type', 'title')

class CommunityNotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'community', 'notification_type', 'title')

class NoticeCommentAdmin(admin.ModelAdmin):
    list_display = ('bcnotice', 'tknotice', 'community', 'message', 'created')

class NoticeStatusAdmin(admin.ModelAdmin):
    list_display = ('bcnotice', 'tknotice', 'community', 'seen', 'status')

admin.site.register(UserNotification, UserNotificationAdmin)
admin.site.register(CommunityNotification, CommunityNotificationAdmin)
admin.site.register(NoticeComment, NoticeCommentAdmin)
admin.site.register(NoticeStatus, NoticeStatusAdmin)
