from django import forms
from .models import *

class AttachLabelForm(forms.ModelForm):
    class Meta:
        model = BCLabel
        fields = ['default_text', 'modified_text']
        widgets = {
            'default_text': forms.Textarea(attrs={'class':'default-label-textarea'}),
            'modified_text': forms.Textarea(attrs={'class': 'implement-labels-textarea'})
        }