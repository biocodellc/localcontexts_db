from django.contrib import admin
from apps.accounts.models import UserInstitution, Institutions, Community, UserCommunity, UserProfile

# Register your models here.
admin.site.register(UserInstitution)
admin.site.register(UserCommunity)
admin.site.register(Institutions)
admin.site.register(Community)
admin.site.register(UserProfile)
