from django.contrib import admin
from .models import Community, UserCommunity, InviteMember, CommunityJoinRequest

admin.site.register(Community)
admin.site.register(UserCommunity)
admin.site.register(InviteMember)
admin.site.register(CommunityJoinRequest)

