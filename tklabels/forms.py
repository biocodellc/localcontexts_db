from django import forms
from .models import *

class CustomizeTKLabelForm(forms.ModelForm):
    class Meta:
        model = TKLabel
        fields = ['default_text', 'audiofile']
        widgets = {
            'default_text': forms.Textarea(attrs={'class': 'w-100 margin-top-1 margin-bottom-2', 'id': 'label-template-text', 'style': 'height: 150px; padding: 10px;'}),
        }

class EditTKLabelForm(forms.ModelForm):
    class Meta:
        model = TKLabel
        fields = ['default_text', 'audiofile']
        widgets = {
            'default_text': forms.Textarea(attrs={'class': 'w-100 margin-top-1 margin-bottom-2', 'id': 'label-template-text', 'style': 'height: 150px; padding: 10px;'}),
        }