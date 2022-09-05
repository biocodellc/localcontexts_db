from django.contrib import admin
from .models import *

class NoticeAdmin(admin.ModelAdmin):
    list_display = ('project', 'notice_type', 'researcher', 'institution', 'created', 'archived' )
    search_fields = ('project',)

class OpenToCollaborateNoticeURLAdmin(admin.ModelAdmin):
    list_display = ('institution', 'researcher', 'name', 'url', 'added')

class LabelTranslationAdmin(admin.ModelAdmin):
    list_display = ('translated_name', 'language', 'language_tag', 'translated_text', )

class EntitiesNotifiedAdmin(admin.ModelAdmin):
    list_display = ('project',)
    search_fields = ('project',)

class ConnectionsAdmin(admin.ModelAdmin):
    list_display = ('community', 'researcher', 'institution')

class LabelVersionAdmin(admin.ModelAdmin):
    list_display = ('version', 'bclabel', 'tklabel', 'created', 'is_approved')
    readonly_fields = ('bclabel', 'tklabel', 'version', 'version_text', 'created_by', 'approved_by', 'created',)

class LabelTranslationVersionAdmin(admin.ModelAdmin):
    list_display = ('version_instance', 'translated_name', 'language', 'created')
    readonly_fields = ('version_instance', 'translated_name', 'language', 'language_tag', 'translated_text', 'created',)

class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('project', 'sender', 'community', 'message', 'created')
    search_fields = ('project',)

class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = ('project', 'community', 'seen', 'status')
    search_fields = ('project',)

# class LabelNoteAdmin(admin.ModelAdmin):
#     list_display = ('bclabel', 'tklabel', 'sender',)

admin.site.register(ProjectComment, ProjectCommentAdmin)
admin.site.register(ProjectStatus, ProjectStatusAdmin)
# admin.site.register(LabelNote, LabelNoteAdmin)
admin.site.register(Notice, NoticeAdmin)
admin.site.register(LabelVersion, LabelVersionAdmin)
admin.site.register(LabelTranslationVersion, LabelTranslationVersionAdmin)
admin.site.register(LabelTranslation, LabelTranslationAdmin)
admin.site.register(EntitiesNotified, EntitiesNotifiedAdmin)
admin.site.register(Connections, ConnectionsAdmin)
admin.site.register(OpenToCollaborateNoticeURL, OpenToCollaborateNoticeURLAdmin)

