from django.contrib import admin
from .models import Project, ProjectContributors, ProjectComment

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_contact', 'project_contact_email', 'is_public', 'date_added')

class ProjectContributorsAdmin(admin.ModelAdmin):
    list_display = ('project', 'institution', 'community', 'researcher')

class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('project', 'sender', 'community', 'message', 'created')

admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectContributors, ProjectContributorsAdmin)
admin.site.register(ProjectComment, ProjectCommentAdmin)