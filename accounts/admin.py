from django.contrib import admin
from .models import Profile, UserCommunity, UserInstitution, SignUpInvitation

admin.site.register(Profile)
admin.site.register(UserCommunity)
admin.site.register(UserInstitution)
admin.site.register(SignUpInvitation)


