from django.contrib import admin
from .models import Project, ProjectContributors, ProjectPerson, ProjectCreator

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_creator', 'project_contact', 'project_contact_email', 'project_privacy', 'project_page', 'date_added', 'unique_id')
    readonly_fields = ('unique_id', 'project_page')

class ProjectContributorsAdmin(admin.ModelAdmin):
    list_display = ('project',)

class ProjectPersonAdmin(admin.ModelAdmin):
    list_display = ('project', 'name', 'email')

class ProjectCreatorAdmin(admin.ModelAdmin):
    list_display = ('project', 'community', 'institution', 'researcher')

admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectContributors, ProjectContributorsAdmin)
admin.site.register(ProjectPerson, ProjectPersonAdmin)
admin.site.register(ProjectCreator, ProjectCreatorAdmin)
