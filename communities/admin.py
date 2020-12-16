from django.contrib import admin
from .models import Community, UserCommunity, InviteMember

admin.site.register(Community)
admin.site.register(UserCommunity)
admin.site.register(InviteMember)

