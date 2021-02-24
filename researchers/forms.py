from django import forms
from .models import Researcher
from projects.models import Project
from bclabels.models import BCNotice
from projects.models import ProjectContributors

class ConnectResearcherForm(forms.ModelForm):
    class Meta:
        model = Researcher
        fields = ['orcid']
        widgets = {
            'orcid': forms.TextInput(attrs={'size': 40}),
        }

class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'is_public', 'project_type', 'description', 'source', 'url', 'publication_date', 'principal_investigator', 'principal_investigator_affiliation', 'project_contact', 'project_contact_email', 'publication_doi', 'project_data_guid', 'recommended_citation', 'geome_project_id']
        widgets = {
            'title': forms.Textarea(attrs={'rows': 1, 'cols':65}),
            'description': forms.Textarea(attrs={'rows': 4, 'cols':65}),
            'source': forms.Textarea(attrs={'rows': 1, 'cols':65}),
            'publication_date': forms.Textarea(attrs={'rows': 1, 'cols':65}),
            'is_public': forms.CheckboxInput(attrs={'class':'is-public-checkbox', 'style': 'width:20px;height:20px;'}),
            'principal_investigator': forms.TextInput(attrs={'size': 65}),
            'principal_investigator_affiliation': forms.TextInput(attrs={'size': 65}),
            'project_contact': forms.TextInput(attrs={'size': 65}),
            'project_contact_email': forms.TextInput(attrs={'size': 65}),
            'publication_doi': forms.TextInput(attrs={'size': 65}),
            'project_data_guid': forms.TextInput(attrs={'size': 65}),
            'recommended_citation': forms.TextInput(attrs={'size': 65}),
            'geome_project_id': forms.TextInput(attrs={'size': 65}),
            'url': forms.TextInput(attrs={'size': 65}),

        }

class UpdateResearcherForm(forms.ModelForm):
    class Meta:
        model = Researcher
        fields = ['orcid', 'contact_email', 'contact_number', 'website']
        widgets = {
            'orcid': forms.TextInput(attrs={'size': 40}),
            'contact_email': forms.TextInput(attrs={'size': 40}),
            'contact_number': forms.TextInput(attrs={'size': 40}),
            'website': forms.TextInput(attrs={'size': 40}),
        }

class ProjectContributorsForm(forms.ModelForm):
    class Meta:
        model = ProjectContributors
        fields = ['community']