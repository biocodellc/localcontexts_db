from django.contrib import admin
from .models import UserNotification, CommunityNotification, InstitutionNotification

class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'community', 'notification_type', 'title')

class CommunityNotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'community', 'notification_type', 'title')

class InstitutionNotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'institution', 'notification_type', 'title')

admin.site.register(UserNotification, UserNotificationAdmin)
admin.site.register(CommunityNotification, CommunityNotificationAdmin)
admin.site.register(InstitutionNotification, InstitutionNotificationAdmin)
