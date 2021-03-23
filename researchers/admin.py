from django.contrib import admin
from .models import Researcher

class ResearcherAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact_email', 'orcid')

admin.site.register(Researcher, ResearcherAdmin)