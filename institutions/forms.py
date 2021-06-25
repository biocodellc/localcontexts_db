from django import forms
from .models import Institution
from django.utils.translation import ugettext_lazy as _

class CreateInstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['institution_id', 'city_or_town', 'state_or_province', 'country', 'contact_name', 'contact_email']
        widgets = {
            'contact_name': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-100'}),
            'city_or_town': forms.TextInput(attrs={'class': 'w-100'}),
            'state_or_province': forms.TextInput(attrs={'class': 'w-100'}),
        }

class CreateInstitutionNoRorForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['institution_name','institution_id', 'city_or_town', 'state_or_province', 'country', 'contact_name', 'contact_email']
        error_messages = {
            'institution_name': {
                'unique': _("An institution by that name already exists."),
            },
        }
        widgets = {
            'contact_name': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-100'}),
            'city_or_town': forms.TextInput(attrs={'class': 'w-100'}),
            'state_or_province': forms.TextInput(attrs={'class': 'w-100'}),
        }

class UpdateInstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['contact_name', 'contact_email', 'city_or_town', 'state_or_province', 'country', 'image']
        widgets = {
            'contact_name': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-100'}),
            'state_or_province': forms.TextInput(attrs={'class': 'w-100'}),
            'city_or_town': forms.TextInput(attrs={'class': 'w-100'}),
        }