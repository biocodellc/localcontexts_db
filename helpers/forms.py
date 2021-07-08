from django import forms
from .models import *
from django.forms import modelformset_factory, inlineformset_factory

AddLabelTranslationFormSet = modelformset_factory(
    LabelTranslation,
    fields=('title', 'language', 'translation', ),
    extra=1,
    widgets = {
            'title': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Translated title'}),
            'language': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Language'}),
            'translation': forms.Textarea(attrs={'class': 'w-100 margin-top-1 margin-bottom-2', 'style': 'height: 150px; padding: 10px;'}),
    }
)

UpdateLabelTranslationFormSet = inlineformset_factory(
    BCLabel, LabelTranslation, 
    fields=('title', 'language', 'translation',),
    extra=0,
    widgets = {
        'title': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Translated title'}),
        'language': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Language'}),
        'translation': forms.Textarea(attrs={'class': 'w-100 margin-top-1 margin-bottom-2', 'style': 'height: 150px; padding: 10px;'}),
    }
)