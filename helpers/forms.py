from django import forms
from .models import *

class AddLabelTranslationForm(forms.ModelForm):
    class Meta:
        model = LabelTranslation
        fields = ['title', 'language', 'translation']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-20', 'placeholder': 'Translated title'}),
            'language': forms.TextInput(attrs={'class': 'w-20', 'placeholder': 'What langauge?'}),
            'translation': forms.Textarea(attrs={'class': 'w-100 margin-top-1 margin-bottom-2', 'style': 'height: 150px; padding: 10px;'}),
        }