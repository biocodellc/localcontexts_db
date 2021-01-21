from django.contrib import admin
from .models import Profile, UserAffiliation, SignUpInvitation

admin.site.register(Profile)
admin.site.register(UserAffiliation)
admin.site.register(SignUpInvitation)


