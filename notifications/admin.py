from django.contrib import admin
from .models import UserNotification, CommunityNotification, InstitutionNotification, ResearcherNotification

class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'community', 'notification_type', 'title', 'created')

class CommunityNotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'community', 'notification_type', 'title', 'created')

class InstitutionNotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'institution', 'notification_type', 'title', 'created')

class ResearcherNotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'researcher', 'notification_type', 'title', 'created')

admin.site.register(UserNotification, UserNotificationAdmin)
admin.site.register(CommunityNotification, CommunityNotificationAdmin)
admin.site.register(InstitutionNotification, InstitutionNotificationAdmin)
admin.site.register(ResearcherNotification, ResearcherNotificationAdmin)
