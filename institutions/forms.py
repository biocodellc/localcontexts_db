from django import forms
from .models import Institution
from django.utils.translation import ugettext_lazy as _

class CreateInstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['institution_id', 'city_town', 'state_province_region', 'country', 'description']
        widgets = {
            'city_town': forms.TextInput(attrs={'class': 'w-100'}),
            'state_province_region': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'class': 'w-100', 'rows': 3,}),
        }

class CreateInstitutionNoRorForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['institution_name','institution_id', 'city_town', 'state_province_region', 'country', 'description']
        error_messages = {
            'institution_name': {
                'unique': _("An institution by that name already exists."),
            },
        }
        widgets = {
            'city_town': forms.TextInput(attrs={'class': 'w-100'}),
            'state_province_region': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'class': 'w-100', 'rows': 3,}),
        }

class ConfirmInstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['contact_name', 'contact_email', 'support_document']
        widgets = {
            'contact_name': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-100', 'required': 'required'}),
        }

class UpdateInstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['contact_name', 'contact_email', 'city_town', 'state_province_region', 'country', 'image', 'description']
        widgets = {
            'contact_name': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-100'}),
            'state_province_region': forms.TextInput(attrs={'class': 'w-100'}),
            'city_town': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'class': 'w-100', 'rows': 3,}),
        }