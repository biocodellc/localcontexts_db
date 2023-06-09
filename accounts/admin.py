from django.contrib import admin
from .models import Profile, UserAffiliation, SignUpInvitation
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

class UserAdminCustom(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name',)

class SignUpInvitationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'email', 'date_sent')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'affiliation', 'is_researcher')
    readonly_fields = ('api_key',)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(UserAffiliation)
admin.site.register(SignUpInvitation, SignUpInvitationAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)



