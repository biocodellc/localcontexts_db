from django.contrib import admin
from apps.accounts.models import UserInstitution, Community, Institution, UserCommunity, UserProfile

# Register your models here.
admin.site.register(UserInstitution)
admin.site.register(UserCommunity)
admin.site.register(Institution)
admin.site.register(Community)
admin.site.register(UserProfile)
