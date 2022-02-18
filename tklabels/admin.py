from django.contrib import admin
from .models import TKLabel

class TKLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'community', 'created_by', 'is_approved', 'created', 'audiofile')
    readonly_fields = ('unique_id', 'created',)

admin.site.register(TKLabel, TKLabelAdmin)