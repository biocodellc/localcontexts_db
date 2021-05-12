from django.contrib import admin
from .models import UserNotification, ActionNotification, NoticeComment

class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'community', 'notification_type', 'title', 'reference_id', 'created')

class ActionNotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'community', 'institution', 'researcher', 'notification_type', 'title', 'created')

class NoticeCommentAdmin(admin.ModelAdmin):
    list_display = ('bcnotice', 'tknotice', 'sender', 'community', 'message', 'created')

admin.site.register(UserNotification, UserNotificationAdmin)
admin.site.register(ActionNotification, ActionNotificationAdmin)
admin.site.register(NoticeComment, NoticeCommentAdmin)
