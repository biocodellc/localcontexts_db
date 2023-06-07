from django import forms
from .models import Institution
from django.utils.translation import ugettext_lazy as _

class CreateInstitutionForm(forms.ModelForm):    
    ror_id = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'institutionIDROR', 'value': ''}))

    class Meta:
        model = Institution
        fields = ['institution_name', 'ror_id', 'city_town', 'state_province_region', 'country', 'description']
        error_messages = {
            'institution_name': {
                'unique': _("An institution by that name already exists."),
            },
        }
        widgets = {
            'institution_name': forms.TextInput(attrs={'id':'organizationInput', 'name':'institution_name', 'class': 'w-100', 'autocomplete': 'off', 'required': True, 'placeholder': 'Search ROR institutions...'}),
            'ror_id': forms.HiddenInput(attrs={'id': 'institutionIDROR', 'value': '', 'required': False}),
            'city_town': forms.TextInput(attrs={'id':'institutionCityTown', 'class': 'w-100'}),
            'state_province_region': forms.TextInput(attrs={'id':'institutionStateProvRegion', 'class': 'w-100'}),
            'description': forms.Textarea(attrs={'class': 'w-100', 'rows': 2, 'required': True}),
            'country': forms.TextInput(attrs={'id':'institutionCountry', 'class': 'w-100', }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        readonly_fields = ['city_town', 'state_province_region', 'country']
        for field_name in readonly_fields:
            self.fields[field_name].widget.attrs['readonly'] = True
            self.fields[field_name].widget.attrs['class'] = 'readonly-input w-100'

class CreateInstitutionNoRorForm(forms.ModelForm):
    is_ror = forms.BooleanField(initial=False, widget=forms.HiddenInput)

    class Meta:
        model = Institution
        fields = ['institution_name', 'city_town', 'state_province_region', 'country', 'description', 'is_ror']
        error_messages = {
            'institution_name': {
                'unique': _("An institution by that name already exists."),
            },
        }
        widgets = {
            'institution_name': forms.TextInput(attrs={'name':'institution_name', 'class': 'w-100', 'autocomplete': 'off', 'required': True}),
            'city_town': forms.TextInput(attrs={'class': 'w-100'}),
            'state_province_region': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'class': 'w-100', 'rows': 2,}),
            'country': forms.TextInput(attrs={'class': 'w-100', }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_ror'].required = False

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