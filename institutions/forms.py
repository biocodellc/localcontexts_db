from django import forms
from .models import Institution

class CreateInstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['institution_name', 'institution_id', 'orcid', 'town_or_city', 'country', 'contact_name', 'contact_email']

class UpdateInstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['institution_name']