from django.contrib import admin
from .models import Community, InviteMember, JoinRequest

class CommunityAdmin(admin.ModelAdmin):
    list_display = ('community_name', 'community_creator', 'contact_name', 'contact_email', 'is_approved', 'created', 'country')
    search_fields = ('community_name', 'contact_name', 'contact_email',)
    readonly_fields = ('native_land_slug',)

class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ('community', 'institution', 'user_from', 'user_to', 'status', 'date_sent')
    search_fields = ('community__community_name', 'institution__institution_name', 'user_from__username',)

class InviteMemberAdmin(admin.ModelAdmin):
    list_display = ('community', 'institution', 'sender', 'receiver', 'role', 'status', 'created')
    search_fields = ('community__community_name', 'institution__institution_name', 'sender__username', 'receiver__username',)

admin.site.register(Community, CommunityAdmin)
admin.site.register(InviteMember, InviteMemberAdmin)
admin.site.register(JoinRequest, JoinRequestAdmin)

