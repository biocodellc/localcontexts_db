from django.contrib import admin
from .models import LabelTranslation

class LabelTranslationAdmin(admin.ModelAdmin):
    list_display = ('language', 'title', 'translation', )

admin.site.register(LabelTranslation, LabelTranslationAdmin)

