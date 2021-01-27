from django.contrib import admin
from .models import Project, Researcher, ProjectContributors

admin.site.register(Project)
admin.site.register(Researcher)
admin.site.register(ProjectContributors)
