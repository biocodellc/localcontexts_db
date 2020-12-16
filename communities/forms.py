from django import forms
from .models import Community, InviteMember

class CreateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['community_name', 'country']

class AddCommunityMember(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['viewers', 'editors']

class InviteMemberForm(forms.ModelForm):
    class Meta:
        model = InviteMember
        fields = ['receiver', 'role']