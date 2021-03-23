from django.contrib import admin
from .models import Community, InviteMember, CommunityJoinRequest

class CommunityAdmin(admin.ModelAdmin):
    list_display = ('community_name', 'community_creator', 'contact_name', 'contact_email', 'is_approved', 'is_publicly_listed')

class CommunityJoinRequestAdmin(admin.ModelAdmin):
    list_display = ( 'target_community', 'user_from', 'user_to', 'status', 'date_sent')

class InviteMemberAdmin(admin.ModelAdmin):
    list_display = ('community', 'sender', 'receiver', 'role', 'status', 'created')

admin.site.register(Community, CommunityAdmin)
admin.site.register(InviteMember, InviteMemberAdmin)
admin.site.register(CommunityJoinRequest, CommunityJoinRequestAdmin)

