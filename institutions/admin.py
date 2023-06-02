from django.contrib import admin
from .models import Institution

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('institution_name', 'institution_creator', 'contact_name', 'contact_email', 'is_approved', 'is_ror', 'created', 'country')
    search_fields = ('institution_name', 'institution_creator__username', 'contact_name', 'contact_email',)

admin.site.register(Institution, InstitutionAdmin)