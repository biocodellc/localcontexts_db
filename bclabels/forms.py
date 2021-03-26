from django import forms
from .models import *

class CustomiseBCLabelForm(forms.ModelForm):
    class Meta:
        model = BCLabel
        fields = ['name', 'default_text']
        widgets = {
            'name': forms.TextInput(attrs={'size': 40, 'id': 'label-title-name'}),
            'default_text': forms.Textarea(attrs={'rows': 4, 'cols': 204, 'id': 'label-template-text'}),
        }

class ApproveAndEditLabelForm(forms.ModelForm):
    class Meta:
        model = BCLabel
        fields = ['name', 'default_text']
        widgets = {
            'name': forms.TextInput(attrs={'size': 40}),
            'default_text': forms.Textarea(attrs={'rows': 4, 'cols': 204}),
        }
