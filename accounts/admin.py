from django.contrib import admin
from .models import Profile, UserAffiliation, SignUpInvitation

class SignUpInvitationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'email', 'date_sent')

admin.site.register(Profile)
admin.site.register(UserAffiliation)
admin.site.register(SignUpInvitation, SignUpInvitationAdmin)


