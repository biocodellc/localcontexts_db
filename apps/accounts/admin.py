from django.contrib import admin
from .models import Community, Institution, UserCommunity, UserInstitution, Role, Project, UserProfile

admin.site.register(Institution)
admin.site.register(Community)
admin.site.register(UserCommunity)
admin.site.register(UserInstitution)
admin.site.register(Role)
admin.site.register(Project)
admin.site.register(UserProfile)

