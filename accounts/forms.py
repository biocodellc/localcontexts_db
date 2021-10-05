from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, SignUpInvitation

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=150, help_text='Required')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        # Cleans the data so nothing harmful can get passed though the form
        user.email = self.cleaned_data['email']

        #if we want to save
        if commit:
            user.save()

        return user

class UserCreateProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

# updating user instance (same as above but includes email)
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'w-100'}),
            'first_name': forms.TextInput(attrs={'class': 'w-100'}),
            'last_name': forms.TextInput(attrs={'class': 'w-100'}),
        }

class ProfileCreationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['position', 'affiliation', 'city_town', 'state_province_region', 'country']
        widgets = {
            'position': forms.TextInput(attrs={'style': 'width: 100%;'}),
            'affiliation': forms.TextInput(attrs={'class': 'w-100'}),
            'city_town': forms.TextInput(attrs={'class': 'w-100'}),
            'state_province_region': forms.TextInput(attrs={'class': 'w-100'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['position', 'affiliation', 'preferred_language', 'city_town', 'state_province_region', 'country']
        widgets = {
            'position': forms.TextInput(attrs={'class': 'w-100'}),
            'affiliation': forms.TextInput(attrs={'class': 'w-100'}),
            'preferred_language': forms.TextInput(attrs={'class': 'w-100'}),
            'city_town': forms.TextInput(attrs={'class': 'w-100'}),
            'state_province_region': forms.TextInput(attrs={'class': 'w-100'}),
        }

class ResendEmailActivationForm(forms.Form):
    email = forms.EmailField(label=_('Email'), required=True, widget=forms.EmailInput(attrs={'class': 'w-100', 'placeholder': 'email@domain.com'}))


class SignUpInvitationForm(forms.ModelForm):
    class Meta:
        model = SignUpInvitation
        fields = ['email', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'cols': 65}),
            'email': forms.TextInput(attrs={'size': 65}),
        }