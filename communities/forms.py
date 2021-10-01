from django import forms
from .models import Community, InviteMember, JoinRequest
from django.utils.translation import ugettext_lazy as _

class CreateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['community_name', 'community_entity', 'state_province_region', 'country', 'description',]
        widgets = {
            'community_name': forms.TextInput(attrs={'class': 'w-100'}),
            'community_entity': forms.TextInput(attrs={'class': 'w-100'}),
            'state_province_region': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-100'}),
        }
        error_messages = {
            'community_name': {
                'unique': _("A community by that name already exists."),
            },
        }

class ConfirmCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['contact_name', 'contact_email', 'support_document']
        widgets = {
            'contact_name': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-100', 'required': 'required'}),
        }

class UpdateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['contact_name', 'contact_email', 'description', 'community_entity', 'city_town', 'state_province_region', 'country', 'image']
        widgets = {
            'community_entity': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_name': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-100'}),
            'state_province_region': forms.TextInput(attrs={'class': 'w-100'}),
            'city_town': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-100'}),
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

class JoinRequestForm(forms.ModelForm):
    class Meta:
        model = JoinRequest
        fields = ['role', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'class':'w-100'}),
        }