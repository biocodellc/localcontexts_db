from .models import *
from django import forms

class CustomizeBCLabelForm(forms.ModelForm):
    class Meta:
        model = BCLabel
        fields = ['name', 'language', 'label_text', 'audiofile']
        widgets = {
            'name': forms.TextInput(attrs={'id': 'label-template-name', 'class': 'w-100', 'autocomplete': 'off'}),
            'language': forms.TextInput(attrs={'class': 'languageListInput w-100', 'placeholder': 'English', 'autocomplete': 'off'}),
            'label_text': forms.Textarea(attrs={'class': 'w-100 margin-top-1 margin-bottom-2', 'id': 'label-template-text', 'style': 'height: 150px; padding: 10px;'}),
        }

class EditBCLabelForm(forms.ModelForm):
    class Meta:
        model = BCLabel
        fields = ['name', 'language', 'label_text', 'audiofile']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-100', 'autocomplete': 'off'}),
            'language': forms.TextInput(attrs={'class': 'languageListInput w-100', 'placeholder': 'English', 'autocomplete': 'off'}),
            'label_text': forms.Textarea(attrs={'class': 'w-100 margin-top-1 margin-bottom-2', 'id': 'label-template-text', 'style': 'height: 150px; padding: 10px;'}),
        }
