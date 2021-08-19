from django import forms
from .models import Researcher

class ConnectResearcherForm(forms.ModelForm):
    class Meta:
        model = Researcher
        fields = ['primary_institution']
        widgets = {
            'primary_institution': forms.TextInput(attrs={'class': 'w-100'}),
        }

class UpdateResearcherForm(forms.ModelForm):
    class Meta:
        model = Researcher
        fields = '__all__'
        exclude = ['user']
        widgets = {
            'contact_email': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_number': forms.TextInput(attrs={'class': 'w-100'}),
            'website': forms.TextInput(attrs={'class': 'w-100'}),
            'primary_institution': forms.TextInput(attrs={'class': 'w-100'}),
        }