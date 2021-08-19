from django.contrib import admin
from .models import Project, ProjectContributors, ProjectPerson

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_creator', 'project_contact', 'project_contact_email', 'project_privacy', 'unique_id')
    readonly_fields = ('unique_id',)

class ProjectContributorsAdmin(admin.ModelAdmin):
    list_display = ('project',)

class ProjectPersonAdmin(admin.ModelAdmin):
    list_display = ('project', 'name', 'email')

admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectContributors, ProjectContributorsAdmin)
admin.site.register(ProjectPerson, ProjectPersonAdmin)
