from django.contrib import admin
from .models import Researcher

class ResearcherAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact_email', 'orcid', 'primary_institution')

admin.site.register(Researcher, ResearcherAdmin)