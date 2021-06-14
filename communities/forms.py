from django import forms
from .models import Community, InviteMember
from django.utils.translation import ugettext_lazy as _

class CreateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['community_name', 'town', 'country', 'contact_name', 'contact_email']
        widgets = {
            'contact_name': forms.TextInput(attrs={'size': 22}),
            'contact_email': forms.EmailInput(attrs={'size': 24}),
        }
        error_messages = {
            'community_name': {
                'unique': _("A community by that name already exists."),
            },
        }

class UpdateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['contact_name', 'contact_email', 'town', 'country', 'is_publicly_listed', 'image']
        widgets = {
            'contact_name': forms.TextInput(attrs={'size': 40}),
            'contact_email': forms.EmailInput(attrs={'size': 40}),
            'town': forms.TextInput(attrs={'size': 40}),
        }

class InviteMemberForm(forms.ModelForm):
    class Meta:
        model = InviteMember
        fields = ['receiver', 'role', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'class':'w-100'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(InviteMemberForm, self).__init__(*args, **kwargs)
        self.fields['receiver'].label_from_instance = lambda obj: "%s" % obj.get_full_name()