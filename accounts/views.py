from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages, auth

from django.contrib.auth.models import User
from django.views.generic import View
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from notifications.models import UserNotification

from .decorators import *
from .models import *
from .forms import *

# Imports for sending emails
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token, email_exists
from django.contrib.sites.shortcuts import get_current_site

@unauthenticated_user
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Remember the current location
            current_site=get_current_site(request)
            template = render_to_string('snippets/activate.html', 
            {
                'user': user,
                'domain':current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user)
            })

            to_email = form.cleaned_data.get('email')

            email_contents = EmailMessage(
                #Email subject
                'Activate Your Account',
                #Body of the email
                template,
                #Sender
                settings.EMAIL_HOST_USER,
                #Recipient, in list to send to multiple addresses at a time.
                [to_email]
            )
            email_contents.fail_silently=False
            email_contents.send()
            return redirect('verify')
    else: 
        form = RegistrationForm()
    
    return render(request, "accounts/register.html", { "form" : form })

@unauthenticated_user
def login(request):
    if request.method == 'POST':
        # email = request.POST['email']
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

    if request.method == 'POST':
        form = ResendEmailActivationForm(request.POST)
        if form.is_valid():
            active_users = User._default_manager.filter(**{
                '%s__iexact' % User.get_email_field_name(): form.cleaned_data['email'],
                'is_active': False,
            })

            if active_users:
                current_site = get_current_site(request)
                email_template = 'snippets/activate.html'
                email_subject = 'Activate Your Account'
                message = render_to_string(email_template, {
                    'user': active_users[0],
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(active_users[0].pk)),
                    'token': generate_token.make_token(active_users[0]),
                })
                active_users[0].email_user(email_subject, message)
                messages.add_message(request, messages.INFO, 'Activation Email Sent!')
                return redirect('verify')

            else:
                messages.add_message(request, messages.ERROR, 'Email did not match any registration email.')
                return redirect('verify')
    else:
        form = ResendEmailActivationForm()
    return render(request, 'accounts/verify.html', {'form': form})
    
@login_required(login_url='login')
def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    n = UserNotification.objects.filter(to_user=request.user)

    user_has_community = UserAffiliation.objects.filter(user=request.user).exists()
    target_communitites = Community.objects.filter(community_creator=request.user)
    target_institutions = Institution.objects.filter(institution_creator=request.user)

    is_user_researcher = Researcher.objects.filter(user=request.user).exists()
    if is_user_researcher:
        researcher = Researcher.objects.get(user=request.user)
    else:
        researcher = False

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
    x = UserAffiliation.objects.get(id=pk)  
    user_communities = x.communities.all()

    context = {
        'target_user': target_user,
        'user_communities': user_communities,
    }
    return render(request, 'accounts/users.html', context)

@login_required(login_url='login')
def create_profile(request):
    if request.method == 'POST':
        user_form = UserCreateProfileForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            # Redirects based on what is selected in the dropdown
            if request.POST.get('registration_reason') == 'community':
                return redirect('connect-community')
            elif request.POST.get('registration_reason') == 'institution':
                return redirect('connect-institution')
            elif request.POST.get('registration_reason') == 'researcher':
                return redirect('connect-researcher')

            return redirect('dashboard')
    else:
        user_form = UserCreateProfileForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

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
    if request.method == "POST":
        invite_form = SignUpInvitationForm(request.POST or None)
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
    else:
        invite_form = SignUpInvitationForm()

    return render(request, 'accounts/invite.html', {'invite_form': invite_form})