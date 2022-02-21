from django.contrib import admin
from .models import BCLabel

class BCLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'community', 'created_by', 'is_approved', 'created',)
    readonly_fields = ('unique_id', 'created',)

admin.site.register(BCLabel, BCLabelAdmin)
