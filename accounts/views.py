from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages, auth
from django.views.generic import View
from django.contrib.auth.views import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user

from django.core.paginator import Paginator

# For emails
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text

from django.contrib.auth.models import User
from communities.models import Community, InviteMember, JoinRequest
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
import datetime

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
                send_welcome_email(user)
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
    n = UserNotification.objects.filter(to_user=request.user)
    researcher = is_user_researcher(request.user)
    user_affiliation = UserAffiliation.objects.prefetch_related('communities', 'institutions').get(user=request.user)

    user_communities = user_affiliation.communities.prefetch_related('admins', 'editors', 'viewers').all()
    user_institutions = user_affiliation.institutions.prefetch_related('admins', 'editors', 'viewers').all()
    profile = Profile.objects.select_related('user').get(user=request.user)

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
    request.user.profile.onboarding_on = True
    request.user.profile.save()
    return redirect('dashboard')

@login_required(login_url='login')
def create_profile(request):
    if request.method == 'POST':
        user_form = UserCreateProfileForm(request.POST, instance=request.user)
        profile_form = ProfileCreationForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('select-account')
    else:
        user_form = UserCreateProfileForm(instance=request.user)
        profile_form = ProfileCreationForm(instance=request.user.profile)

    context = { 'user_form': user_form, 'profile_form': profile_form,}
    return render(request, 'accounts/create-profile.html', context)

@login_required(login_url='login')
def update_profile(request):
    profile = Profile.objects.select_related('user').get(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
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
    affiliations = UserAffiliation.objects.prefetch_related('communities', 'institutions').get(user=request.user)
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
        p = Paginator(c, 5)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)
        context = { 'communities': True, 'items': page }
        return render(request, 'accounts/registry.html', context)
    except:
        raise Http404()

# REGISTRY : INSTITUTIONS
def registry_institutions(request):
    try:
        i = Institution.approved.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').all().order_by('institution_name')
        p = Paginator(i, 5)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)

        context = { 'institutions': True, 'items': page,}
        return render(request, 'accounts/registry.html', context)
    except:
        raise Http404()

# REGISTRY : RESEARCHERS
def registry_researchers(request):
    try:
        r = Researcher.objects.select_related('user').all().order_by('user__username')
        p = Paginator(r, 5)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)

        context = { 'researchers': True, 'items': page,}
        return render(request, 'accounts/registry.html', context)
    except:
        raise Http404()

# Hub stats page
def hub_counter(request):
    current_datetime = datetime.datetime.now()
    otc_notices = OpenToCollaborateNoticeURL.objects.all()

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

    if dev_prod_or_local(request.get_host()) == 'PROD':
        admin = User.objects.get(id=1)
        researcher = Researcher.objects.none()
        if Researcher.objects.filter(user=admin).exists():
            researcher = Researcher.objects.get(user=admin)


        # Registered
        # exclude any account created by admin
        community_count = Community.objects.exclude(community_creator=1).count() # sample community
        institution_count = Institution.objects.exclude(institution_creator=1).count() # sample institution
        researcher_count = Researcher.objects.exclude(user=1).count() # admin's researcher account
        reg_total = community_count + institution_count + researcher_count

        # Notices
        for notice in Notice.objects.exclude(researcher=researcher, institution=1):
            if notice.notice_type == 'biocultural':
                bc_notice_count += 1
            if notice.notice_type == 'traditional_knowledge':
                tk_notice_count += 1
            if notice.notice_type == 'attribution_incomplete':
                attr_notice_count += 1
        notices_total = bc_notice_count + tk_notice_count + attr_notice_count

        # Project Counts -- excludes accounts created by ADMIN
        # Community projects
        for community in Community.objects.exclude(community_creator=admin):
            comm_count = ProjectCreator.objects.filter(community=community).count()
            community_projects += comm_count
        
        # Institution projects
        for institution in Institution.objects.exclude(institution_creator=admin):
            inst_count = ProjectCreator.objects.filter(institution=institution).count()
            institution_projects += inst_count

        # Researcher projects
        for researcher in Researcher.objects.exclude(user=admin):
            res_count = ProjectCreator.objects.filter(researcher=researcher).count()
            researcher_projects += res_count

        projects_count = community_projects + institution_projects + researcher_projects

        # Labels
        bclabels_count = BCLabel.objects.exclude(created_by=admin).count()
        tklabels_count = TKLabel.objects.exclude(created_by=admin).count()
        total_labels = bclabels_count + tklabels_count

    else:
        # Registered, everyone's account is shown
        community_count = Community.objects.count() 
        institution_count = Institution.objects.count() 
        researcher_count = Researcher.objects.count()
        reg_total = community_count + institution_count + researcher_count

        # Notices
        for notice in Notice.objects.all():
            if notice.notice_type == 'biocultural':
                bc_notice_count += 1
            if notice.notice_type == 'traditional_knowledge':
                tk_notice_count += 1
            if notice.notice_type == 'attribution_incomplete':
                attr_notice_count += 1
        notices_total = bc_notice_count + tk_notice_count + attr_notice_count

        # Project Counts -- excludes accounts created by ADMIN
        # Community projects
        for community in Community.objects.all():
            comm_count = ProjectCreator.objects.filter(community=community).count()
            community_projects += comm_count
        
        # Institution projects
        for institution in Institution.objects.all():
            inst_count = ProjectCreator.objects.filter(institution=institution).count()
            institution_projects += inst_count

        # Researcher projects
        for researcher in Researcher.objects.all():
            res_count = ProjectCreator.objects.filter(researcher=researcher).count()
            researcher_projects += res_count

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
        'current_datetime': current_datetime,

        'otc_notices': otc_notices,
    }
    
    return render(request, 'accounts/totals-count.html', context)
