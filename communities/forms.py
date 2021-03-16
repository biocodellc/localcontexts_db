from django import forms
from .models import Community, InviteMember
from .utils import checkif_community_in_user_community, checkif_invite_exists

class CreateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['community_name', 'town', 'country', 'contact_name', 'contact_email']
        widgets = {
            'contact_name': forms.TextInput(attrs={'size': 22}),
            'contact_email': forms.EmailInput(attrs={'size': 24}),
        }

class UpdateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['community_name', 'contact_name', 'contact_email', 'town', 'country', 'is_publicly_listed']
        widgets = {
            'community_name': forms.TextInput(attrs={'size': 40}),
            'contact_name': forms.TextInput(attrs={'size': 40}),
            'contact_email': forms.EmailInput(attrs={'size': 40}),
            'town': forms.TextInput(attrs={'size': 40}),
        }

class InviteMemberForm(forms.ModelForm):
    class Meta:
        model = InviteMember
        fields = ['receiver', 'role', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'cols':70}),
        }
    
    def __init__(self, *args, **kwargs):
        super(InviteMemberForm, self).__init__(*args, **kwargs)
        self.fields['receiver'].label_from_instance = lambda obj: "%s" % obj.get_full_name() + " " + obj.email