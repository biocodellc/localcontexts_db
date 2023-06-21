from django.contrib import admin
from .models import BCLabel

class BCLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'community', 'created_by', 'language_tag', 'language', 'is_approved', 'created',)
    readonly_fields = ('unique_id', 'created', 'version',)
    search_fields = ('name', 'community__community_name', 'created_by__username',)

admin.site.register(BCLabel, BCLabelAdmin)
