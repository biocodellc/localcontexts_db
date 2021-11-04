from django import forms
from .models import *

class CustomizeBCLabelForm(forms.ModelForm):
    class Meta:
        model = BCLabel
        fields = ['default_text']
        widgets = {
            'default_text': forms.Textarea(attrs={'class': 'w-100 margin-top-1 margin-bottom-2', 'id': 'label-template-text', 'style': 'height: 150px; padding: 10px;'}),
        }

class EditBCLabelForm(forms.ModelForm):
    class Meta:
        model = BCLabel
        fields = ['default_text']
        widgets = {
            'default_text': forms.Textarea(attrs={'class': 'w-100 margin-top-1 margin-bottom-2', 'id': 'label-template-text', 'style': 'height: 150px; padding: 10px;'}),
        }
