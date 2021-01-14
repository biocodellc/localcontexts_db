from django.contrib import admin
from .models import Community, InviteMember, CommunityJoinRequest

admin.site.register(Community)
admin.site.register(InviteMember)
admin.site.register(CommunityJoinRequest)

