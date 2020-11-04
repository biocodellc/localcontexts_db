from django.shortcuts import render, redirect
from django.contrib import messages, auth

from django.contrib.auth.models import User
from django.views.generic import View
from .models import Profile
from .forms import UserUpdateForm, ProfileUpdateForm

# Imports for sending emails
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
from django.contrib.sites.shortcuts import get_current_site

def register(request):
    if request.method == 'POST':
        #Get form values
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        #Check for password match
        if password == password2:
            #Check that username exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'That username is taken')
                return redirect('register')
            else:
                #Check that email exists
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'That email is being used')
                    return redirect('register')
                else:
                    # If data unique, create user
                    user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
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
                    email_contents = EmailMessage(
                        #Email subject
                        'Activate Your Account',
                        #Body of the email
                        template,
                        #Sender
                        settings.EMAIL_HOST_USER,
                        #Recipient, in list to send to multiple addresses at a time.
                        [email]
                    )
                    email_contents.fail_silently=False
                    email_contents.send()
                    return redirect('verify')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
    else:
        return render(request, "accounts/register.html")

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
                return render(request, 'accounts/create-profile.html')
            else:
                auth.login(request, user)
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Credentials')
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
        return render(request, 'snippets/activate_failed.html', status=401)

def verify(request):
    return render(request, 'accounts/verify.html')
    
@login_required
def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('index')

@login_required
def dashboard(request):
    return render(request, "accounts/dashboard.html")

@login_required
def create_profile(request):
    if request.method == 'POST':
        #TODO: add classes to input instances so it's easier to style
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, 
                                         request.FILES, 
                                         instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # TODO: Change this based on what is selected in dropdown.
            return redirect('dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'accounts/create-profile.html', context)

@login_required
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
            return redirect('update-profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/update-profile.html', context)

@login_required
def connect_institution(request):
    return render(request, 'accounts/connect-institution.html')

@login_required
def connect_community(request):
    return render(request, 'accounts/connect-community.html')