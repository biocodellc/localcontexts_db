from django.contrib import admin
from .models import UserNotification, CommunityNotification

admin.site.register(UserNotification)
admin.site.register(CommunityNotification)
