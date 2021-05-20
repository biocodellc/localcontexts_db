from django import forms
from .models import Researcher
from bclabels.models import BCNotice

class ConnectResearcherForm(forms.ModelForm):
    class Meta:
        model = Researcher
        fields = ['associated_institution', 'location', 'orcid']
        widgets = {
            'associated_institution': forms.TextInput(attrs={'size': 40}),
            'orcid': forms.TextInput(attrs={'size': 40}),
        }

class UpdateResearcherForm(forms.ModelForm):
    class Meta:
        model = Researcher
        fields = '__all__'
        exclude = ['user']
        widgets = {
            'orcid': forms.TextInput(attrs={'size': 40}),
            'contact_email': forms.TextInput(attrs={'size': 40}),
            'contact_number': forms.TextInput(attrs={'size': 40}),
            'website': forms.TextInput(attrs={'size': 40}),
            'associated_institution': forms.TextInput(attrs={'size': 40}),
            'location': forms.TextInput(attrs={'size': 40}),
        }