from django.contrib import admin
from .models import Researcher

class ResearcherAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact_email', 'orcid', 'primary_institution', 'date_connected')
    search_fields = ('contact_email', 'user__username', 'orcid', 'primary_institution', 'date_connected')
    readonly_fields = ('orcid_auth_token',)

admin.site.register(Researcher, ResearcherAdmin)