from django.contrib import admin
from .models import Project, ProjectContributors

admin.site.register(Project)
admin.site.register(ProjectContributors)