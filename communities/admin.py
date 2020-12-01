from django.contrib import admin
from .models import Community, UserCommunity, CommunityMembers

admin.site.register(Community)
admin.site.register(CommunityMembers)
admin.site.register(UserCommunity)
