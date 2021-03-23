from django.contrib import admin
from .models import TKLabel, TKNotice

class TKNoticeAdmin(admin.ModelAdmin):
    list_display = ('project', 'placed_by_researcher', 'placed_by_institution', 'created')

class TKLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'community', 'created_by', 'is_approved', 'created')

admin.site.register(TKLabel, TKLabelAdmin)
admin.site.register(TKNotice, TKNoticeAdmin)