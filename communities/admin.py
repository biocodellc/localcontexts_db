from django.contrib import admin
from .models import Community, InviteMember, JoinRequest

class CommunityAdmin(admin.ModelAdmin):
    list_display = ('community_name', 'community_creator', 'contact_name', 'contact_email', 'is_approved', 'created')
    search_fields = ('community_name', 'contact_name', 'contact_email',)
    readonly_fields = ('native_land_slug',)

class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ( 'community', 'institution', 'user_from', 'user_to', 'status', 'date_sent')

class InviteMemberAdmin(admin.ModelAdmin):
    list_display = ('community', 'institution', 'sender', 'receiver', 'role', 'status', 'created')

admin.site.register(Community, CommunityAdmin)
admin.site.register(InviteMember, InviteMemberAdmin)
admin.site.register(JoinRequest, JoinRequestAdmin)

