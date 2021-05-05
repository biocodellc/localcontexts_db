from django import forms
from .models import Institution

class CreateInstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['institution_name', 'institution_id', 'orcid', 'town_or_city', 'country', 'contact_name', 'contact_email']

class UpdateInstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['institution_name', 'contact_name', 'contact_email', 'town_or_city', 'country', 'image']
        widgets = {
            'institution_name': forms.TextInput(attrs={'size': 30}),
            'contact_name': forms.TextInput(attrs={'size': 30}),
            'contact_email': forms.EmailInput(attrs={'size': 40}),
        }