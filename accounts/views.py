from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages, auth
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
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

from django.contrib.auth.models import User
from communities.models import Community, InviteMember
from institutions.models import Institution
from researchers.models import Researcher
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from helpers.models import Notice, OpenToCollaborateNoticeURL
from notifications.models import UserNotification
from projects.models import Project, ProjectCreator

from localcontexts.utils import dev_prod_or_local
from researchers.utils import is_user_researcher
from helpers.utils import accept_member_invite

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

        # If user is found, log in the user.
        if user is not None:
            if not user.last_login:
                auth.login(request, user)
                # Welcome email
                send_welcome_email(request, user)
                return redirect('create-profile')
            else:
                auth.login(request, user)
                return redirect('dashboard')
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
    n = UserNotification.objects.filter(to_user=user)
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

    profile = user.user_profile

    if request.method == 'POST':
        profile.onboarding_on = False
        profile.save()

    context = { 
        'profile': profile,
        'user_communities': user_communities,
        'user_institutions': user_institutions,
        'researcher': researcher,
        'notifications': n,
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
                # Save invitation instance
                data.save()
                return redirect('invite')
    return render(request, 'accounts/invite.html', {'invite_form': invite_form})

# REGISTRY : COMMUNITIES
def registry_communities(request):
    try:
        # Paginate the query of all approved communities
        c = Community.approved.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').all().order_by('community_name')
        if request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('community_name')
                query = SearchQuery(q)
                results = c.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None
            
        p = Paginator(c, 5)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)
        context = { 'communities': True, 'items': page, 'results': results }
        return render(request, 'accounts/registry.html', context)
    except:
        raise Http404()

# REGISTRY : INSTITUTIONS
def registry_institutions(request):
    try:
        i = Institution.approved.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').all().order_by('institution_name')
        if request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('institution_name')
                query = SearchQuery(q)
                results = i.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        p = Paginator(i, 5)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)

        context = { 'institutions': True, 'items': page, 'results': results}
        return render(request, 'accounts/registry.html', context)
    except:
        raise Http404()

# REGISTRY : RESEARCHERS
def registry_researchers(request):
    try:
        r = Researcher.objects.select_related('user').all().order_by('user__username')
        if request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('user__username', 'user__first_name', 'user__last_name')
                query = SearchQuery(q)
                results = r.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        p = Paginator(r, 5)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)

        context = { 'researchers': True, 'items': page, 'results': results}
        return render(request, 'accounts/registry.html', context)
    except:
        raise Http404()

# Hub stats page
def hub_counter(request):
    otc_notices = OpenToCollaborateNoticeURL.objects.select_related('researcher', 'institution').all()

    reg_total = 0
    notices_total = 0

    bc_notice_count = 0
    tk_notice_count = 0
    attr_notice_count = 0

    community_count = 0
    institution_count = 0
    researcher_count = 0

    community_projects = 0
    institution_projects = 0
    researcher_projects = 0

    bclabels_count = 0
    tklabels_count = 0
    total_labels = 0

    projects_count = 0

    # Registered accounts
    community_count = Community.objects.count() 
    institution_count = Institution.objects.count() 
    researcher_count = Researcher.objects.count()
    reg_total = community_count + institution_count + researcher_count

    # Notices
    bc_notice_count = Notice.objects.filter(notice_type="biocultural").count()
    tk_notice_count = Notice.objects.filter(notice_type="traditional_knowledge").count()
    attr_notice_count = Notice.objects.filter(notice_type="attribution_incomplete").count()
    notices_total = bc_notice_count + tk_notice_count + attr_notice_count

    # How many projects were created by which account
    for project in ProjectCreator.objects.select_related('institution', 'community', 'researcher').all():
        if project.institution:
            institution_projects += 1
        if project.community:
            community_projects += 1
        if project.researcher:
            researcher_projects += 1

    projects_count = community_projects + institution_projects + researcher_projects

    # Labels
    bclabels_count = BCLabel.objects.count()
    tklabels_count = TKLabel.objects.count()
    total_labels = bclabels_count + tklabels_count


    context = {
        'community_count': community_count,
        'researcher_count': researcher_count,
        'institution_count': institution_count,
        'reg_total': reg_total,

        'bc_notice_count': bc_notice_count,
        'tk_notice_count': tk_notice_count,
        'attr_notice_count': attr_notice_count,
        'notices_total': notices_total,

        'community_projects': community_projects,
        'institution_projects': institution_projects,
        'researcher_projects': researcher_projects,
        'projects_count': projects_count,

        'bclabels_count': bclabels_count,
        'tklabels_count': tklabels_count, 
        'total_labels': total_labels,

        'otc_notices': otc_notices,
    }
    
    return render(request, 'accounts/totals-count.html', context)

def manage_mailing_list(request, first_name):
    selections = request.POST.getlist('topic')
    tech = 'no'
    news = 'no'
    events = 'no'
    notices = 'no'
    labels = 'no'
    for item in selections:
        if item == 'tech':
            tech = 'yes'
        if item == 'news':
            news = 'yes'
        if item == 'events':
            events = 'yes'
        if item == 'notices':
            notices = 'yes'
        if item == 'labels':
            labels = 'yes'
    variables= '{"first_name":"%s", "tech": "%s", "news": "%s", "events": "%s","notices": "%s","labels": "%s"}'%(first_name, tech, news, events, notices, labels)
    return(variables)

def subscription_form(request):
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
            return redirect('subscription-form')
        else:
            if result['success']:
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                name= str(first_name) + str(' ') + str(last_name)
                email = request.POST['email']
                variables = manage_mailing_list(request, first_name)
                add_to_mailing_list(str(email), str(name), str(variables))
                messages.add_message(request, messages.SUCCESS, 'You have been subscribed.')
                return redirect('subscription-form')
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')

    return render(request, 'accounts/subscription-form.html')

def unsubscribe_form(request, emailb64):
    email=force_text(urlsafe_base64_decode(emailb64))
    response = get_member_info(email)
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
            if item == 'notices':
                notices = variables[item]
            if item == 'labels':
                labels = variables[item]
            if item == 'first_name':
                first_name = variables[item]
    
        context={
            'email':email,
            'tech': tech,
            'news': news,
            'events': events,
            'notices': notices,
            'labels': labels,
            'subscribed':subscribed
        }
    else:
        context={'subscribed':subscribed}

    if request.method == 'POST':
        if 'updatebtn' in request.POST:
            if 'topic' not in request.POST:
                messages.add_message(request, messages.ERROR, 'Please select at least one topic.')
                return redirect('unsubscribe-form')
            else:
                variables = manage_mailing_list(request, first_name)
                add_to_mailing_list(str(email), str(name), str(variables))
                messages.add_message(request, messages.SUCCESS, 'Your preferences have been updated.')
                return redirect('unsubscribe-form')

        if 'unsubscribebtn' in request.POST:
            if 'unsubscribe' not in request.POST:
                messages.add_message(request, messages.ERROR, 'Please check the box below to unsubscribe.')
                return redirect('unsubscribe-form')
            else:
                unsubscribe_from_mailing_list(str(email), str(name))
                return redirect('unsubscribe-form')
    return render(request, 'accounts/unsubscribe-form.html', context)

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