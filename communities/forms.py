from django import forms
from .models import Community

class CreateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['community_name', 'country']

class AddCommunityMember(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['members']