from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, SignUpInvitation

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField(required=True, max_length=150, help_text='Required')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        # Cleans the data so nothing harmful can get passed though the form
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        #if we want to save
        if commit:
            user.save()

        return user

class UserCreateProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

# updating user instance (same as above but includes email)
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['job_title', 'city_or_town', 'country']

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