from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages, auth
from django.views.generic import View
from django.contrib.auth.views import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user
from rest_framework_api_key.models import APIKey

from django.core.paginator import Paginator

# For emails
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text

from unidecode import unidecode
from django.db.models import Q

from django.contrib.auth.models import User
from communities.models import Community, InviteMember
from institutions.models import Institution
from researchers.models import Researcher
from helpers.models import HubActivity
from projects.models import Project

from localcontexts.utils import dev_prod_or_local
from researchers.utils import is_user_researcher
from helpers.utils import accept_member_invite

from helpers.emails import *
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

                if User.objects.filter(email=user.email).exists():
                    messages.error(request, 'A user with this email already exists')
                    return redirect('register')
                else:
                    user.is_active = False
                    user.save()

                    # If SignupInvite instances exist, delete them
                    if SignUpInvitation.objects.filter(email=user.email).exists():
                        for invite in SignUpInvitation.objects.filter(email=user.email):
                            invite.delete()

                    send_activation_email(request, user)
                    HubActivity.objects.create(
                        action_user_id=user.id,
                        action_type="New User"
                    )
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
    envi = dev_prod_or_local(request.get_host())

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
        next_path = get_next_path(request, default_path='dashboard')

        # If user is found, log in the user.
        if user is not None:
            if not user.last_login:
                auth.login(request, user)
                # Welcome email
                send_welcome_email(request, user)
                return redirect('create-profile')
            else:
                auth.login(request, user)
                return redirect(next_path)
        else:
            messages.error(request, 'Your username or password does not match an account')
            return redirect('login')
    else:
        return render(request, "accounts/login.html", {'envi': envi })
    
@login_required(login_url='login')
def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('login')

def landing(request):
    return redirect('login')

@login_required(login_url='login')
def select_account(request):
    return render(request, 'accounts/select-account.html')

@login_required(login_url='login')
def dashboard(request):
    user = request.user
    profile = user.user_profile
    researcher = is_user_researcher(user)

    affiliation = user.user_affiliations.prefetch_related(
        'communities', 
        'institutions', 
        'communities__admins', 
        'communities__editors', 
        'communities__viewers',
        'institutions__admins', 
        'institutions__editors', 
        'institutions__viewers'
        ).all().first()

    user_communities = affiliation.communities.all()    
    user_institutions = affiliation.institutions.all()

    if request.method == 'POST':
        profile.onboarding_on = False
        profile.save()

    context = { 
        'profile': profile,
        'user_communities': user_communities,
        'user_institutions': user_institutions,
        'researcher': researcher,
    }
    return render(request, "accounts/dashboard.html", context)

@login_required(login_url='login')
def onboarding_on(request):
    request.user.user_profile.onboarding_on = True
    request.user.user_profile.save()
    return redirect('dashboard')

@login_required(login_url='login')
def create_profile(request):
    if request.method == 'POST':
        user_form = UserCreateProfileForm(request.POST, instance=request.user)
        profile_form = ProfileCreationForm(request.POST, instance=request.user.user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('select-account')
    else:
        user_form = UserCreateProfileForm(instance=request.user)
        profile_form = ProfileCreationForm(instance=request.user.user_profile)

    context = { 'user_form': user_form, 'profile_form': profile_form,}
    return render(request, 'accounts/create-profile.html', context)

@login_required(login_url='login')
def update_profile(request):
    profile = Profile.objects.select_related('user').get(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.user_profile)
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
        profile_form = ProfileUpdateForm(instance=request.user.user_profile)

    context = { 'profile': profile, 'user_form': user_form, 'profile_form': profile_form }
    return render(request, 'accounts/update-profile.html', context)

@login_required(login_url='login')
def change_password(request):
    profile = Profile.objects.select_related('user').get(user=request.user)

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
    return render(request, 'accounts/change-password.html', {'profile': profile, 'form':form })
    

@login_required(login_url='login')
def deactivate_user(request):
    profile = Profile.objects.select_related('user').get(user=request.user)
    if request.method == "POST":
        user = request.user
        user.is_active = False
        user.save()
        auth.logout(request)
        messages.add_message(request, messages.INFO, 'Your account has been deactivated.')
        return redirect('login')
    return render(request, 'accounts/deactivate.html', { 'profile': profile })

@login_required(login_url='login')
def manage_organizations(request):
    profile = Profile.objects.select_related('user').get(user=request.user)
    affiliations = UserAffiliation.objects.prefetch_related('communities', 'institutions', 'communities__community_creator', 'institutions__institution_creator').get(user=request.user)
    researcher = Researcher.objects.none()
    users_name = get_users_name(request.user)
    if Researcher.objects.filter(user=request.user).exists():
        researcher = Researcher.objects.get(user=request.user)
    return render(request, 'accounts/manage-orgs.html', { 'profile': profile, 'affiliations': affiliations, 'researcher': researcher, 'users_name': users_name })

@login_required(login_url='login')
def member_invitations(request):
    profile = Profile.objects.select_related('user').get(user=request.user)
    member_invites = InviteMember.objects.filter(receiver=request.user)

    if request.method == 'POST':
        invite_id = request.POST.get('invite_id')
        accept_member_invite(request, invite_id)
        return redirect('member-invitations')

    context = {
        'profile': profile,
        'member_invites': member_invites,
    }
    return render(request, 'accounts/member-invitations.html', context)

@login_required(login_url='login')
def delete_member_invitation(request, pk):
    profile = Profile.objects.select_related('user').get(user=request.user)
    member_invites = InviteMember.objects.filter(receiver=request.user)

    target_member_invite = InviteMember.objects.get(id=pk)
    target_member_invite.delete()

    context = {
        'profile': profile,
        'member_invites': member_invites,
    }
    return render(request, 'accounts/member-invitations.html', context)

@login_required(login_url='login')
def invite_user(request):
    # use internally referred path, otherwise use the default path
    default_path = 'invite'
    referred_path = request.headers.get('Referer', default_path)
    selected_path = urllib.parse.urlparse(referred_path).path

    invite_form = SignUpInvitationForm(request.POST or None)
    if request.method == "POST":
        if invite_form.is_valid():
            data = invite_form.save(commit=False)
            data.sender = request.user

            if User.objects.filter(email=data.email).exists():
                messages.add_message(request, messages.ERROR, 'This user is already in the Hub')
                return redirect(selected_path)
            else: 
                if SignUpInvitation.objects.filter(email=data.email).exists():
                    messages.add_message(request, messages.ERROR, 'An invitation has already been sent to this email')
                    return redirect(selected_path)
                else:
                    messages.add_message(request, messages.SUCCESS, 'Invitation Sent')
                    send_invite_user_email(request, data)
                    data.save()
                    return redirect(selected_path)

    # when validation fails and selected_path is not the default
    # redirect to selected path
    if selected_path.strip('/') != default_path:
        return redirect(selected_path)

    return render(request, 'accounts/invite.html', {'invite_form': invite_form})

def registry(request, filtertype=None):
    try:
        c = Community.approved.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').all().order_by('community_name')
        i = Institution.approved.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').all().order_by('institution_name')
        r = Researcher.objects.select_related('user').all().order_by('user__username')

        if ('q' in request.GET) and (filtertype != None):
            q = request.GET.get('q')
            return redirect('/registry/?q=' + q)
        
        elif ('q' in request.GET) and (filtertype == None):
            q = request.GET.get('q')
            q = unidecode(q) #removes accents from search query

            # Filter's accounts by the search query, showing results that match with or without accents
            c = c.filter(community_name__unaccent__icontains=q)
            i = i.filter(institution_name__unaccent__icontains=q)
            r = r.filter(Q(user__username__unaccent__icontains=q) | Q(user__first_name__unaccent__icontains=q) | Q(user__last_name__unaccent__icontains=q))

            cards = return_registry_accounts(c, r, i)

            p = Paginator(cards, 5)

        else:
            if filtertype == 'communities':
                cards = c
            elif filtertype == 'institutions':
                cards = i
            elif filtertype == 'researchers':
                cards = r
            elif filtertype == 'otc':
                researchers_with_otc = r.filter(otc_researcher_url__isnull=False).distinct()
                institutions_with_otc = i.filter(otc_institution_url__isnull=False).distinct()
                cards = return_registry_accounts(None, researchers_with_otc, institutions_with_otc)
            else:
                cards = return_registry_accounts(c, r, i)

            p = Paginator(cards, 5)

        page_num = request.GET.get('page', 1)
        page = p.page(page_num)

        context = {
            'researchers' : r,
            'communities' : c,
            'institutions' : i,
            'items' : page,
            'filtertype' : filtertype
        }
        
        return render(request, 'accounts/registry.html', context)

    except:
        raise Http404()

def projects_board(request, filtertype=None):
    try:
        approved_institutions = Institution.objects.filter(is_approved=True).values_list('id', flat=True)
        approved_communities = Community.objects.filter(is_approved=True).values_list('id', flat=True)
        projects = Project.objects.filter(
            Q(project_privacy='Public'),
            Q(project_creator_project__institution__in=approved_institutions) |
            Q(project_creator_project__community__in=approved_communities) |
            Q(project_creator_project__researcher__user__isnull=False)
        ).select_related('project_creator').order_by('-date_modified')

        if ('q' in request.GET) and (filtertype != None):
            q = request.GET.get('q')
            return redirect('/projects-board/?q=' + q)
        elif ('q' in request.GET) and (filtertype == None):
            q = request.GET.get('q')
            q = unidecode(q) #removes accents from search query

            # Filter's accounts by the search query, showing results that match with or without accents
            results = projects.filter(Q(title__unaccent__icontains=q) | Q(description__unaccent__icontains=q))

            p = Paginator(results, 10)
        else:
            if filtertype == 'labels':
                results = projects.filter(Q(bc_labels__isnull=False) | Q(tk_labels__isnull=False))
            elif filtertype == 'notices':
                results = projects.filter(project_notice__archived=False).distinct()
            else:
                results = projects

            p = Paginator(results, 10)

        page_num = request.GET.get('page', 1)
        page = p.page(page_num)

        context = {
            'projects': projects,
            'items': page,
            'filtertype' : filtertype
        }
        return render(request, 'accounts/projects-board.html', context)
    except:
        raise Http404()


# Hub stats page
def hub_counter(request):
    return redirect('/admin/dashboard/')

def newsletter_subscription(request):
    environment = dev_prod_or_local(request.get_host())

    if environment == 'PROD' or 'localhost' in request.get_host():
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

        if request.method == 'POST':
            if 'topic' not in request.POST:
                messages.add_message(request, messages.ERROR, 'Please select at least one topic.')
                return redirect('newsletter-subscription')
            else:
                if result['success']:
                    first_name = request.POST['first_name']
                    last_name = request.POST['last_name']
                    name= str(first_name) + str(' ') + str(last_name)
                    email = request.POST['email']
                    emailb64 = urlsafe_base64_encode(force_bytes(email))
                    variables = manage_mailing_list(request, first_name, emailb64)
                    add_to_mailing_list(str(email), str(name), str(variables))
                    messages.add_message(request, messages.SUCCESS, 'You have been subscribed.')
                    return redirect('newsletter-unsubscription', emailb64=emailb64)
                else:
                    messages.error(request, 'Invalid reCAPTCHA. Please try again.')

        return render(request, 'accounts/newsletter-subscription.html')
    else:
        return redirect('login')

def newsletter_unsubscription(request, emailb64):
    environment = dev_prod_or_local(request.get_host())

    if environment == 'PROD' or 'localhost' in request.get_host():
        try:
            email=force_text(urlsafe_base64_decode(emailb64))
            response = get_newsletter_member_info(email)
            data=response.json()
            member_info = data["member"]
            name = member_info["name"]
            variables = member_info["vars"]
            subscribed = member_info["subscribed"]
            if subscribed == True:
                for item in variables:
                    if item == 'tech':
                        tech = variables[item]
                    if item == 'news':
                        news = variables[item]
                    if item == 'events':
                        events = variables[item]
                    if item == 'notice':
                        notice = variables[item]
                    if item == 'labels':
                        labels = variables[item]
                    if item == 'first_name':
                        first_name = variables[item]
            
                context = {
                    'email': email,
                    'tech': tech,
                    'news': news,
                    'events': events,
                    'notice': notice,
                    'labels': labels,
                    'subscribed': subscribed
                }
            else:
                context = {'subscribed' : subscribed}

            if request.method == 'POST':
                if 'updatebtn' in request.POST:
                    if 'topic' not in request.POST:
                        messages.add_message(request, messages.ERROR, 'Please select at least one topic.')
                        return redirect('newsletter-unsubscription', emailb64=emailb64)
                    else:
                        variables = manage_mailing_list(request, first_name, email)
                        add_to_mailing_list(str(email), str(name), str(variables))
                        messages.add_message(request, messages.SUCCESS, 'Your preferences have been updated.')
                        return redirect('newsletter-unsubscription', emailb64=emailb64)

                if 'unsubscribebtn' in request.POST:
                    if 'unsubscribe' not in request.POST:
                        messages.add_message(request, messages.ERROR, 'Please check the box below to unsubscribe.')
                        return redirect('newsletter-unsubscription', emailb64=emailb64)
                    else:
                        unsubscribe_from_mailing_list(str(email), str(name))
                        return redirect('newsletter-unsubscription', emailb64=emailb64)
            return render(request, 'accounts/newsletter-unsubscription.html', context)
        except:
            raise Http404()

    else:
        return redirect('login')

@login_required(login_url='login')
def api_keys(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        if 'generatebtn' in request.POST:
            api_key, key = APIKey.objects.create_key(name=request.user.username)
            profile.api_key = key
            profile.save()
            messages.add_message(request, messages.SUCCESS, 'API Key Generated!')
            page_key = profile.api_key
            return redirect('api-key')

        elif 'hidebtn' in request.POST:
            return redirect('api-key')

        elif 'continueKeyDeleteBtn' in request.POST:
            api_key = APIKey.objects.get(name=request.user.username)
            api_key.delete()
            profile.api_key = None
            profile.save()
            messages.add_message(request, messages.SUCCESS, 'API Key Deleted!')
            return redirect('api-key')

        elif 'copybtn' in request.POST:
            messages.add_message(request, messages.SUCCESS, 'Copied!')
            return redirect('api-key')

        elif 'showbtn' in request.POST:
            page_key = profile.api_key
            context = { 'api_key': page_key, 'has_key': True}
            request.session['keyvisible'] = True
            return redirect('api-key')

    keyvisible = request.session.pop('keyvisible',False)

    if request.method == 'GET':
        if profile.api_key is None:
            context = {'has_key': False}
            return render(request, 'accounts/apikey.html', context)
        elif profile.api_key is not None and keyvisible is not False:
            context = {'has_key': True, 'keyvisible': keyvisible, 'api_key': profile.api_key}
            return render(request, 'accounts/apikey.html', context)
        else:
            context = {'api_key': '**********************************', 'has_key': True}
            return render(request, 'accounts/apikey.html', context)