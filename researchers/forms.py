from django import forms
from .models import Researcher, Project
from bclabels.models import BCNotice
from researchers.models import ProjectContributors

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
        fields = ['title', 'is_public', 'description', 'source', 'publication_date']
        widgets = {
            'title': forms.Textarea(attrs={'rows': 1, 'cols':65}),
            'description': forms.Textarea(attrs={'rows': 4, 'cols':65}),
            'source': forms.Textarea(attrs={'rows': 1, 'cols':65}),
            'publication_date': forms.Textarea(attrs={'rows': 1, 'cols':65}),
            'is_public': forms.CheckboxInput(attrs={'class':'is-public-checkbox', 'style': 'width:20px;height:20px;'}),
        }

class ProjectContributorsForm(forms.ModelForm):
    class Meta:
        model = ProjectContributors
        fields = ['community']