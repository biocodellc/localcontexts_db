from django import forms
from .models import *

class CustomizeTKLabelForm(forms.ModelForm):
    class Meta:
        model = TKLabel
        fields = ['name', 'default_text']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-100', 'id': 'label-title-name'}),
            'default_text': forms.Textarea(attrs={'class': 'w-100 margin-top-1 margin-bottom-2', 'id': 'label-template-text', 'style': 'height: 150px; padding: 10px;'}),
        }

class ApproveAndEditTKLabelForm(forms.ModelForm):
    class Meta:
        model = TKLabel
        fields = ['name', 'default_text']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-100'}),
            'default_text': forms.Textarea(attrs={'class': 'w-100 margin-top-1 margin-bottom-2', 'id': 'label-template-text', 'style': 'height: 150px; padding: 10px;'}),
        }