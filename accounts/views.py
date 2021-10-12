from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages, auth
from django.views.generic import View
from django.contrib.auth.views import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user

# For emails
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text

from django.contrib.auth.models import User
from communities.models import Community, JoinRequest
from institutions.models import Institution
from notifications.models import UserNotification

from researchers.utils import is_user_researcher

from helpers.emails import *
from .models import *
from .forms import *

# Captcha validation imports
import urllib
import json

@unauthenticated_user
def register(request):
    form = RegistrationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            # h/t: https://simpleisbetterthancomplex.com/tutorial/2017/02/21/how-to-add-recaptcha-to-django-site.html
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req =  urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            ''' End reCAPTCHA validation '''

            if result['success']:
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                send_activation_email(request, user)
                return redirect('verify')
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            
            return redirect('register')
    return render(request, "accounts/register.html", { "form" : form })

class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid=force_text(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None

        if user is not None and generate_token.check_token(user, token):
            user.is_active=True
            user.save()
            messages.add_message(request, messages.INFO, 'Profile activation successful. You may now log in.')
            return redirect('login')
        return render(request, 'snippets/activate-failed.html', status=401)

@unauthenticated_user
def verify(request):
    if not request.user.is_anonymous:
        return HttpResponseRedirect('/dashboard')

    form = ResendEmailActivationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            active_users = User._default_manager.filter(**{
                '%s__iexact' % User.get_email_field_name(): form.cleaned_data['email'],
                'is_active': False,
            })

            if active_users:
                resend_activation_email(request, active_users)
                messages.add_message(request, messages.INFO, 'Activation Email Sent!')
                return redirect('verify')
            else:
                messages.add_message(request, messages.ERROR, 'Email did not match any registration email.')
                return redirect('verify')
    return render(request, 'accounts/verify.html', {'form': form})

@unauthenticated_user
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(request, username=username, password=password)

        # If user is found, log in the user.
        if user is not None:
            if not user.last_login:
                auth.login(request, user)
                # Welcome email
                send_welcome_email(user)
                return redirect('create-profile')
            else:
                auth.login(request, user)
                return redirect('dashboard')
        else:
            messages.error(request, 'Your username or password does not match an account')
            return redirect('login')
    else:
        return render(request, "accounts/login.html")
    
@login_required(login_url='login')
def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('login')

def landing(request):
    return redirect('login')

@login_required(login_url='login')
def registration_reason(request):
    return render(request, 'accounts/select-account.html')

@login_required(login_url='login')
def dashboard(request):
    n = UserNotification.objects.filter(to_user=request.user)

    user_has_community = UserAffiliation.objects.filter(user=request.user).exists()
    target_communitites = Community.objects.filter(community_creator=request.user)
    target_institutions = Institution.objects.filter(institution_creator=request.user)

    researcher = is_user_researcher(request.user)

    target_user = UserAffiliation.objects.get(user=request.user)

    # Checks to see if any communities have been created by the current user 
    for x in target_communitites:
        target_user.communities.add(x.id)    # and adds them to the UserAffiliation instance
        target_user.save()
    
    for y in target_institutions:
        target_user.institutions.add(y.id)
        target_user.save()

    if user_has_community:
        current_user = UserAffiliation.objects.get(user=request.user)
        user_communities = current_user.communities.all()
        user_institutions = current_user.institutions.all()

        context = { 
            'current_user': current_user,
            'user_communities': user_communities,
            'user_institutions': user_institutions,
            'researcher': researcher,
            'notifications': n,
        }
        return render(request, "accounts/dashboard.html", context)
    else:
        return render(request, "accounts/dashboard.html")

@login_required(login_url='login')
def create_profile(request):
    if request.method == 'POST':
        user_form = UserCreateProfileForm(request.POST, instance=request.user)
        profile_form = ProfileCreationForm(
            request.POST,  
            instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            return redirect('select-account')
    else:
        user_form = UserCreateProfileForm(instance=request.user)
        profile_form = ProfileCreationForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'accounts/create-profile.html', context)

@login_required(login_url='login')
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.add_message(request, messages.SUCCESS, 'Profile Updated!')
            return redirect('update-profile')
        else:
            messages.add_message(request, messages.ERROR, 'Something went wrong')
            return redirect('update-profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/update-profile.html', context)

@login_required(login_url='login')
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.add_message(request, messages.SUCCESS, 'Password Successfully Changed!')
            return redirect('change-password')
        else:
            messages.add_message(request, messages.ERROR, 'Something went wrong')
            return redirect('change-password')
    return render(request, 'accounts/change-password.html', {'form':form,})
    

@login_required(login_url='login')
def deactivate_user(request):
    if request.method == "POST":
        user = request.user
        user.is_active = False
        user.save()
        auth.logout(request)
        messages.add_message(request, messages.INFO, 'Your account has been deactivated.')
        return redirect('login')
    return render(request, 'accounts/deactivate.html')

@login_required(login_url='login')
def manage_organizations(request):
    return render(request, 'accounts/manage-orgs.html')

@login_required(login_url='login')
def invite_user(request):
    invite_form = SignUpInvitationForm(request.POST or None)
    if request.method == "POST":
        if invite_form.is_valid():
            data = invite_form.save(commit=False)
            data.sender = request.user
            email_exists = User.objects.filter(email=data.email).exists()

            if email_exists:
                messages.add_message(request, messages.INFO, 'This email is already in use')
                return redirect('invite')
            else: 
                messages.add_message(request, messages.SUCCESS, 'Invitation Sent!')
                send_invite_user_email(request, data)
                return redirect('invite')
    return render(request, 'accounts/invite.html', {'invite_form': invite_form})

def organization_registry(request):
    communities = Community.objects.filter(is_approved=True)
    institutions = Institution.objects.filter(is_approved=True)

    if request.user.is_authenticated:
        user_institutions = UserAffiliation.objects.get(user=request.user).institutions.all()
        user_communities = UserAffiliation.objects.get(user=request.user).communities.all()

        if request.method == 'POST':
            inst_btn_id = request.POST.get('instid')
            comm_btn_id = request.POST.get('commid')

            if inst_btn_id:
                target_institution = Institution.objects.get(id=inst_btn_id)
                main_admin = target_institution.institution_creator

                join_request = JoinRequest.objects.create(user_from=request.user, institution=target_institution, user_to=main_admin)
                join_request.save()

            if comm_btn_id:
                target_community = Community.objects.get(id=comm_btn_id)
                main_admin = target_community.community_creator

                req = JoinRequest.objects.create(user_from=request.user, community=target_community, user_to=main_admin)
                req.save()
            
            return redirect('organization-registry')


        context = {
            'communities': communities,
            'institutions': institutions,
            'user_institutions': user_institutions,
            'user_communities': user_communities,
        }
        return render(request, 'accounts/registry.html', context)

    context = {
        'communities': communities,
        'institutions': institutions,
    }
    return render(request, 'accounts/registry.html', context)

