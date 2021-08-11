from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages, auth
from django.views.generic import View

from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user

# For emails
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from helpers.emails import send_activation_email, resend_activation_email, generate_token

from django.contrib.auth.models import User
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from notifications.models import UserNotification

from .models import *
from .forms import *
from .utils import *

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

                to_email = form.cleaned_data.get('email')
                send_activation_email(request, user, to_email)
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
            messages.add_message(request, messages.INFO, 'Account activation successful. You may now log in.')
            return redirect('login')
        return render(request, 'snippets/activate-failed.html', status=401)

@unauthenticated_user
def verify(request):
    if not request.user.is_anonymous:
        return HttpResponseRedirect('/accounts/dashboard/')

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
def users_view(request, pk):
    target_user = User.objects.get(id=pk)
    x = UserAffiliation.objects.get(user=target_user) 
    user_communities = x.communities.all()
    researcher = is_user_researcher(target_user)

    if request.user == target_user:
        return redirect('dashboard')
    else:
        context = {
            'target_user': target_user,
            'user_communities': user_communities,
            'researcher': researcher,
        }
        return render(request, 'accounts/users.html', context)

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
    #TODO: add a password reset form
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
        'profile_form': profile_form
    }
    return render(request, 'accounts/update-profile.html', context)

@login_required(login_url='login')
def invite_user(request):
    invite_form = SignUpInvitationForm(request.POST or None)
    if request.method == "POST":
        if invite_form.is_valid():
            obj = invite_form.save(commit=False)
            obj.sender = request.user
            check_email = email_exists(obj.email)

            if check_email == True:
                messages.add_message(request, messages.INFO, 'This email is already in use')
                return redirect('invite')
            else: 
                messages.add_message(request, messages.SUCCESS, 'Invitation Sent!')
                current_site=get_current_site(request)
                template = render_to_string('snippets/invite-new-user.html', { 
                    'obj': obj, 
                    'domain': current_site.domain, 
                })

                send_mail(
                    "You've been invited to join the Local Contexts Hub",
                    template,
                    settings.EMAIL_HOST_USER,
                    [obj.email],
                    fail_silently=False)
                
                return redirect('invite')
    return render(request, 'accounts/invite.html', {'invite_form': invite_form})