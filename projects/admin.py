from django.contrib import admin
from .models import *

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_creator', 'project_contact', 'project_contact_email', 'project_privacy', 'project_page', 'date_added', 'unique_id')
    readonly_fields = ('unique_id', 'project_page')
    search_fields = ('title', 'unique_id', 'project_creator__username', 'project_contact', 'project_contact_email',)

class ProjectContributorsAdmin(admin.ModelAdmin):
    list_display = ('project',)
    search_fields = ('project__title',)

class ProjectPersonAdmin(admin.ModelAdmin):
    list_display = ('project', 'name', 'email')

class ProjectCreatorAdmin(admin.ModelAdmin):
    list_display = ('project', 'community', 'institution', 'researcher')
    search_fields = ('project__title',)

class ProjectActivityAdmin(admin.ModelAdmin):
    list_display = ('project', 'date', 'activity')    
    readonly_fields = ('project', 'date', 'activity')
    search_fields = ('project__title',)

class ProjectArchivedAdmin(admin.ModelAdmin):
    list_display = ('project_uuid', 'archived', 'community_id', 'institution_id', 'researcher_id')

class ProjectNoteAdmin(admin.ModelAdmin):
    list_display = ('project', 'community')

admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectContributors, ProjectContributorsAdmin)
admin.site.register(ProjectPerson, ProjectPersonAdmin)
admin.site.register(ProjectCreator, ProjectCreatorAdmin)
admin.site.register(ProjectActivity, ProjectActivityAdmin)
admin.site.register(ProjectArchived, ProjectArchivedAdmin)
admin.site.register(ProjectNote, ProjectNoteAdmin)
