from django import forms
import datetime
from .models import Project, ProjectContributors, ProjectComment

class DateInput(forms.DateInput):
    input_type = 'date'

class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'is_public', 'project_type', 'description', 'url', 'publication_date', 'project_contact', 'project_contact_email', 'publication_doi', 'project_data_guid', 'recommended_citation', 'geome_project_id']
        widgets = {
            'publication_date': DateInput(),
            'title': forms.TextInput(attrs={'size' :65}),
            'description': forms.Textarea(attrs={'rows': 4, 'cols':65}),
            'is_public': forms.CheckboxInput(attrs={'class':'is-public-checkbox', 'style': 'width:20px;height:20px;'}),
            'project_contact': forms.TextInput(attrs={'size': 65}),
            'project_contact_email': forms.TextInput(attrs={'size': 65}),
            'publication_doi': forms.TextInput(attrs={'size': 65}),
            'project_data_guid': forms.TextInput(attrs={'size': 65}),
            'recommended_citation': forms.TextInput(attrs={'size': 65}),
            'geome_project_id': forms.TextInput(attrs={'size': 65}),
            'url': forms.TextInput(attrs={'size': 65}),
        }

class ProjectContributorsForm(forms.ModelForm):
    class Meta:
        model = ProjectContributors
        fields = ['community']

class ProjectCommentForm(forms.ModelForm):
    class Meta:
        model = ProjectComment
        fields = ['message']
        widgets = {
            'message': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Add Comment'})
        }