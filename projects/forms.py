from django import forms
from django.forms import modelformset_factory
import datetime
from .models import Project, ProjectContributors, ProjectPerson
from django.utils.translation import ugettext_lazy as _

class CreateProjectForm(forms.ModelForm):
    PRIVACY = (
        ('Public', 'Public: Can be seen by anyone within and outside of the Local Contexts Hub'),
        ('Discoverable', 'Discoverable: Can be seen by authenticated contributors of the project only'),
        ('Private', 'Private: Can only be seen by project creator'),
    )
    TYPES = (
        ('Item', 'Item'),
        ('Collection', 'Collection'),
        ('Sample', 'Sample'),
        ('Expedition', 'Expedition'),
        ('Publication', 'Publication'),
        ('Exhibition', 'Exhibition'),
        ('Other', 'Other'),
    )
    project_privacy = forms.ChoiceField(label=_('What is the privacy level of this project?'), choices=PRIVACY, widget=forms.RadioSelect())
    project_type = forms.ChoiceField(label=_('What type of project are you creating?*'), choices=TYPES, widget=forms.Select(attrs={'class': 'w-100',}))

    class Meta:
        model = Project
        fields = ['title', 'project_type', 'project_privacy', 'description', 'url', 'project_contact', 'project_contact_email', 'publication_doi', 'project_data_guid', 'recommended_citation']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-100'}),
            'project_contact': forms.TextInput(attrs={'class': 'w-100'}),
            'project_contact_email': forms.TextInput(attrs={'class': 'w-100'}),
            'publication_doi': forms.TextInput(attrs={'class': 'w-100'}),
            'project_data_guid': forms.TextInput(attrs={'class': 'w-100'}),
            'recommended_citation': forms.Textarea(attrs={'rows': 4, 'class': 'w-100'}),
            'url': forms.TextInput(attrs={'class': 'w-100'}),
        }

ProjectPersonFormset = modelformset_factory(
    ProjectPerson,
    fields=('name', 'email' ),
    extra=1,
    widgets = {
        'name': forms.TextInput(attrs={'size': 35, 'placeholder': 'Contributor name'}),
        'email': forms.EmailInput(attrs={'size': 35, 'placeholder': 'Contributor email'}),
    }
)

class EditProjectForm(forms.ModelForm):
    PRIVACY = (
        ('Public', 'Public: Can be seen by anyone within and outside of the Local Contexts Hub'),
        ('Discoverable', 'Discoverable: Can be seen by authenticated contributors of the project only'),
        ('Private', 'Private: Can only be seen by project creator'),
    )
    TYPES = (
        ('Item', 'Item'),
        ('Collection', 'Collection'),
        ('Sample', 'Sample'),
        ('Expedition', 'Expedition'),
        ('Publication', 'Publication'),
        ('Exhibition', 'Exhibition'),
        ('Other', 'Other'),
    )
    project_privacy = forms.ChoiceField(label=_('What is the privacy level of this project?'), choices=PRIVACY, widget=forms.RadioSelect())
    project_type = forms.ChoiceField(label=_('What type of project are you creating?*'), choices=TYPES, widget=forms.Select(attrs={'class': 'w-100',}))

    class Meta:
        model = Project
        fields = ['title', 'project_type', 'project_privacy', 'description', 'url', 'project_contact', 'project_contact_email', 'publication_doi', 'project_data_guid', 'recommended_citation']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-100'}),
            'project_contact': forms.TextInput(attrs={'class': 'w-100'}),
            'project_contact_email': forms.TextInput(attrs={'class': 'w-100'}),
            'publication_doi': forms.TextInput(attrs={'class': 'w-100'}),
            'project_data_guid': forms.TextInput(attrs={'class': 'w-100'}),
            'recommended_citation': forms.Textarea(attrs={'rows': 4, 'class': 'w-100'}),
            'url': forms.TextInput(attrs={'class': 'w-100'}),
        }