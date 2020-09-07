from django.contrib import admin
from database.models import UserInstitution, UserCommunity, Institutions, Community

# Register your models here.
admin.site.register(UserInstitution)
admin.site.register(UserCommunity)
admin.site.register(Institutions)
admin.site.register(Community)