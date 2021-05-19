from django.contrib import admin
from .models import Project, ProjectContributors

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_contact', 'project_contact_email', 'is_public', 'created')
    readonly_fields = ('unique_id', 'created')

class ProjectContributorsAdmin(admin.ModelAdmin):
    list_display = ('project', 'institution', 'community', 'researcher')

admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectContributors, ProjectContributorsAdmin)
