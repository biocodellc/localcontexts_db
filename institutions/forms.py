from django import forms
from .models import Institution
from django.utils.translation import ugettext_lazy as _

class CreateInstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['institution_id', 'orcid', 'town_or_city', 'country', 'contact_name', 'contact_email']
        widgets = {
            'contact_name': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-100'}),
        }

class CreateInstitutionNoRorForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['institution_name','institution_id', 'orcid', 'town_or_city', 'country', 'contact_name', 'contact_email']
        error_messages = {
            'institution_name': {
                'unique': _("An institution by that name already exists."),
            },
        }
        widgets = {
            'contact_name': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-100'}),
            'town_or_city': forms.TextInput(attrs={'class': 'w-100'}),
        }

class UpdateInstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['institution_name', 'contact_name', 'contact_email', 'town_or_city', 'country', 'image']
        widgets = {
            'institution_name': forms.TextInput(attrs={'size': 30}),
            'contact_name': forms.TextInput(attrs={'size': 30}),
            'contact_email': forms.EmailInput(attrs={'size': 40}),
        }