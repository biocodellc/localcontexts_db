from django.contrib import admin
from .models import Institution

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('institution_name', 'institution_creator', 'contact_name', 'contact_email', 'town_or_city', 'country')

admin.site.register(Institution, InstitutionAdmin)
