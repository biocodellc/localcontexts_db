from django import forms
from django.forms import modelformset_factory
import datetime
from .models import Project, ProjectContributors, ProjectPerson

class DateInput(forms.DateInput):
    input_type = 'date'

class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'project_type', 'description', 'url', 'publication_date', 'publication_date_ongoing', 'project_contact', 'project_contact_email', 'publication_doi', 'project_data_guid', 'recommended_citation']
        widgets = {
            'publication_date': DateInput(),
            'title': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-100'}),
            'publication_date_ongoing': forms.CheckboxInput(),
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
    class Meta:
        model = Project
        fields = ['title', 'project_type', 'description', 'url', 'publication_date', 'publication_date_ongoing', 'project_contact', 'project_contact_email', 'publication_doi', 'project_data_guid', 'recommended_citation']
        widgets = {
            'publication_date': DateInput(),
            'title': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-100'}),
            'publication_date_ongoing': forms.CheckboxInput(),
            'project_contact': forms.TextInput(attrs={'class': 'w-100'}),
            'project_contact_email': forms.TextInput(attrs={'class': 'w-100'}),
            'publication_doi': forms.TextInput(attrs={'class': 'w-100'}),
            'project_data_guid': forms.TextInput(attrs={'class': 'w-100'}),
            'recommended_citation': forms.Textarea(attrs={'rows': 4, 'class': 'w-100'}),
            'url': forms.TextInput(attrs={'class': 'w-100'}),
        }