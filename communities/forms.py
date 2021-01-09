from django import forms
from .models import Community, InviteMember
from .utils import checkif_community_in_user_community, checkif_invite_exists

class CreateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['community_name', 'country']

class UpdateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['community_name', 'contact_name', 'contact_email', 'town', 'country', 'is_publicly_listed']

class InviteMemberForm(forms.ModelForm):
    class Meta:
        model = InviteMember
        fields = ['receiver', 'role', 'message']
    
    def __init__(self, *args, **kwargs):
        super(InviteMemberForm, self).__init__(*args, **kwargs)
        self.fields['receiver'].label_from_instance = lambda obj: "%s" % obj.get_full_name() + " " + obj.email