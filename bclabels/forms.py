from django import forms
from .models import *

class CustomiseLabelForm(forms.ModelForm):
    class Meta:
        model = BCLabel
        fields = ['name', 'default_text']
        widgets = {
            'name': forms.TextInput(attrs={'size': 40, 'id': 'bclabel-title'}),
            'default_text': forms.Textarea(attrs={'rows': 4, 'cols': 204, 'id': 'bclabel-template'}),
        }

class ApproveAndEditLabelForm(forms.ModelForm):
    class Meta:
        model = BCLabel
        fields = ['name', 'default_text']
        widgets = {
            'name': forms.TextInput(attrs={'size': 40}),
            'default_text': forms.Textarea(attrs={'rows': 4, 'cols': 204}),
        }
