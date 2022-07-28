from django.contrib import admin
from .models import TKLabel

class TKLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'community', 'created_by', 'language_tag', 'language', 'is_approved', 'created')
    readonly_fields = ('unique_id', 'created', 'version',)

admin.site.register(TKLabel, TKLabelAdmin)