from email.policy import default
from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from .models import Project, ProjectContributors, ProjectPerson
from django.utils.translation import ugettext_lazy as _

class CreateProjectForm(forms.ModelForm):
    PRIVACY = (
        ('Public', 'Public: Anyone with the project link can view all the project information.'),
        ('Discoverable', 'Contributor View: Anyone with the link can view the project unique identifier and any Labels or Notices attached.'),
        ('Private', 'Private: Only the project creator can see the project information.'),
    )
    TYPES = (
        ('Item', 'Item'),
        ('Collection', 'Collection'),
        ('Samples', 'Samples'),
        ('Expedition', 'Expedition'),
        ('Publication', 'Publication'),
        ('Exhibition', 'Exhibition'),
        ('Other', 'Other'),
    )
    project_privacy = forms.ChoiceField(label=_('Who can view this project?'), choices=PRIVACY, initial='Public', widget=forms.RadioSelect(attrs={'class': 'ul-no-bullets'}))
    project_type = forms.ChoiceField(label=_('What is your project type? *'), choices=TYPES, widget=forms.Select(attrs={'class': 'w-100',}))

    class Meta:
        model = Project
        fields = ['title', 'project_type', 'other_type', 'project_privacy', 'description', 'url', 'project_contact', 'project_contact_email', 'providers_id', 'publication_doi', 'project_data_guid']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-100'}),
            'other_type': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Specify other Project type'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-100'}),
            'project_contact': forms.TextInput(attrs={'class': 'w-100'}),
            'project_contact_email': forms.TextInput(attrs={'class': 'w-100'}),
            'publication_doi': forms.TextInput(attrs={'class': 'w-100'}),
            'project_data_guid': forms.TextInput(attrs={'class': 'w-100'}),
            'providers_id': forms.TextInput(attrs={'class': 'w-100'}),
            'url': forms.TextInput(attrs={'class': 'w-100'}),
        }

# Create Project Person
ProjectPersonFormset = modelformset_factory(
    ProjectPerson,
    fields=('name', 'email' ),
    extra=1,
    widgets = {
        'name': forms.TextInput(attrs={'size': 35, 'placeholder': 'Contributor name'}),
        'email': forms.EmailInput(attrs={'size': 35, 'placeholder': 'Contributor email'}),
    },
    can_delete=True
)

# Edit Project Person
ProjectPersonFormsetInline = inlineformset_factory(
    Project, 
    ProjectPerson, 
    extra=1,
    fields=('name', 'email'),
    widgets = {
        'name': forms.TextInput(attrs={'size': 35, 'placeholder': 'Contributor name'}),
        'email': forms.EmailInput(attrs={'size': 35, 'placeholder': 'Contributor email'}),
    },
)

class EditProjectForm(forms.ModelForm):
    PRIVACY = (
        ('Public', 'Public: Can be seen by anyone within and outside of the Local Contexts Hub'),
        ('Discoverable', 'Contributor View: Anyone with the link can view the project unique identifier and any Labels or Notices attached.'),
        ('Private', 'Private: Only the project creator can see the project information.'),
    )
    TYPES = (
        ('Item', 'Item'),
        ('Collection', 'Collection'),
        ('Samples', 'Samples'),
        ('Expedition', 'Expedition'),
        ('Publication', 'Publication'),
        ('Exhibition', 'Exhibition'),
        ('Other', 'Other'),
    )
    project_privacy = forms.ChoiceField(label=_('Who can view this project?'), choices=PRIVACY, widget=forms.RadioSelect())
    project_type = forms.ChoiceField(label=_('What is your project type? *'), choices=TYPES, widget=forms.Select(attrs={'class': 'w-100',}))

    class Meta:
        model = Project
        fields = ['title', 'project_type', 'other_type', 'project_privacy', 'description', 'url', 'project_contact', 'project_contact_email', 'publication_doi', 'project_data_guid', 'providers_id']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-100'}),
            'other_type': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Specify other Project type'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-100'}),
            'project_contact': forms.TextInput(attrs={'class': 'w-100'}),
            'project_contact_email': forms.TextInput(attrs={'class': 'w-100'}),
            'publication_doi': forms.TextInput(attrs={'class': 'w-100'}),
            'project_data_guid': forms.TextInput(attrs={'class': 'w-100'}),
            'providers_id': forms.TextInput(attrs={'class': 'w-100'}),
            'url': forms.TextInput(attrs={'class': 'w-100'}),
        }