from django import forms
from .models import Researcher
from django.utils.translation import ugettext_lazy as _

class ConnectResearcherForm(forms.ModelForm):
    class Meta:
        model = Researcher
        fields = ['primary_institution', 'description']
        widgets = {
            'primary_institution': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'class': 'w-100', 'rows': 2,}),
        }

class UpdateResearcherForm(forms.ModelForm):
    PRIVACY = (
        ('True', 'Yes: Users of the hub can contact me using this email'),
        ('False', 'No: Users of the hub can not contact me using this email'),
    )

    contact_email_public = forms.ChoiceField(label=_('Can this email be used for users of the Local Contexts Hub to contact you?'), choices=PRIVACY, initial='False', widget=forms.RadioSelect(attrs={'class': 'ul-no-bullets'}))

    class Meta:
        model = Researcher
        fields = ['primary_institution', 'contact_email', 'contact_email_public', 'website', 'description', 'image']
        exclude = ['user']
        widgets = {
            'contact_email': forms.TextInput(attrs={'class': 'w-100'}),
            'website': forms.TextInput(attrs={'class': 'w-100'}),
            'primary_institution': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'class': 'w-100', 'rows': 3,}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-100 hide', 'id': 'researcherImgUploadBtn', 'onchange': 'showFileName()'}),

        }