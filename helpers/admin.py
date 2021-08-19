from django.contrib import admin
from .models import Notice, LabelTranslation, NoticeComment, NoticeStatus

class NoticeAdmin(admin.ModelAdmin):
    list_display = ('project', 'notice_type', 'placed_by_researcher', 'placed_by_institution', 'created', )

class LabelTranslationAdmin(admin.ModelAdmin):
    list_display = ('language', 'title', 'translation', )

class NoticeCommentAdmin(admin.ModelAdmin):
    list_display = ('bcnotice', 'tknotice', 'sender', 'community', 'message', 'created')

class NoticeStatusAdmin(admin.ModelAdmin):
    list_display = ('bcnotice', 'tknotice', 'community', 'seen', 'status')

admin.site.register(Notice, NoticeAdmin)
admin.site.register(LabelTranslation, LabelTranslationAdmin)
admin.site.register(NoticeComment, NoticeCommentAdmin)
admin.site.register(NoticeStatus, NoticeStatusAdmin)

