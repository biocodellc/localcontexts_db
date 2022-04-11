from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages, auth
from django.views.generic import View
from django.contrib.auth.views import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.contrib.auth.decorators import login_required

from projects.models import Project
from .decorators import unauthenticated_user

# For emails
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text

from django.contrib.auth.models import User
from communities.models import Community, JoinRequest
from institutions.models import Institution
from researchers.models import Researcher
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from helpers.models import Notice
from notifications.models import UserNotification

from researchers.utils import is_user_researcher

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
        return render(request, "accounts/login.html")
    
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
    print(request.META.get('HTTP_REFERER'))
    return render(request, 'accounts/manage-orgs.html', { 'profile': profile, 'affiliations': affiliations })

# @login_required(login_url='login')
# def remove_organizations(request, org_id):
#     profile = Profile.objects.select_related('user').get(user=request.user)
#     affiliations = UserAffiliation.objects.prefetch_related('communities', 'institutions').get(user=request.user)
#     return redirect('manage-orgs')

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

def organization_registry(request):
    communities = Community.approved.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').all().order_by('community_name')
    institutions = Institution.approved.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').all().order_by('institution_name')
    researchers = Researcher.objects.select_related('user').all()

    if request.user.is_authenticated:
        user_affiliations = UserAffiliation.objects.prefetch_related('institutions', 'communities').get(user=request.user)
        user_institutions = user_affiliations.institutions.all()
        user_communities = user_affiliations.communities.all()

        form = ContactOrganizationForm(request.POST or None)

        if request.method == 'POST':
            if 'contact_btn' in request.POST:
                # contact community or institution
                if form.is_valid():
                    to_email = ''
                    from_name = form.cleaned_data['name']
                    from_email = form.cleaned_data['email']
                    message = form.cleaned_data['message']

                    # which institution or community
                    inst_contact_id = request.POST.get('instid_contact')
                    comm_contact_id = request.POST.get('commid_contact')

                    if inst_contact_id:
                        inst = Institution.objects.select_related('institution_creator').get(id=inst_contact_id)
                        to_email = inst.institution_creator.email
                    
                    if comm_contact_id:
                        comm = Community.objects.select_related('community_creator').get(id=comm_contact_id)
                        to_email = comm.community_creator.email
                    
                    send_contact_email(to_email, from_name, from_email, message)
            else:
                # Request To Join community or institution
                inst_input_id = request.POST.get('instid')
                comm_input_id = request.POST.get('commid')

                if inst_input_id:
                    target_institution = Institution.objects.select_related('institution_creator').get(id=inst_input_id)
                    main_admin = target_institution.institution_creator
                    JoinRequest.objects.create(user_from=request.user, institution=target_institution, user_to=main_admin)

                    # Send email to institution creator
                    send_join_request_email_admin(request, target_institution)

                elif comm_input_id:
                    target_community = Community.objects.select_related('community_creator').get(id=comm_input_id)
                    main_admin = target_community.community_creator
                    JoinRequest.objects.create(user_from=request.user, community=target_community, user_to=main_admin)

                    # Send email to community creator
                    send_join_request_email_admin(request, target_community)

            messages.add_message(request, messages.SUCCESS, 'Your message was sent!')
            return redirect('organization-registry')
        else:
            context = {
                'communities': communities,
                'institutions': institutions,
                'researchers': researchers,
                'user_institutions': user_institutions,
                'user_communities': user_communities,
                'form': form,
            }
            return render(request, 'accounts/registry.html', context)
    
    context = {
        'communities': communities,
        'institutions': institutions,
    }
    return render(request, 'accounts/registry.html', context)

# Hub stats page
def hub_counter(request):
    # Registered
    community_count = Community.objects.count() -  1 # sample community
    institution_count = Institution.objects.count() - 1 # sample institution
    researcher_count = Researcher.objects.count() - 1 # admin's researcher account
    reg_total = community_count + institution_count + researcher_count

    # Notices
    bc_notice_count = 0
    tk_notice_count = 0
    for notice in Notice.objects.all():
        if notice.notice_type == 'biocultural':
            bc_notice_count += 1
        if notice.notice_type == 'traditional_knowledge':
            tk_notice_count += 1
        if notice.notice_type == 'biocultural_and_traditional_knowledge':
            bc_notice_count += 1
            tk_notice_count += 1
            
    notices_total = bc_notice_count + tk_notice_count

    # Projects
    community_projects = 0
    institution_projects = 0
    researcher_projects = 0

    # Community projects
    for community in Community.objects.prefetch_related('projects').all():
        comm_count = community.projects.count()
        community_projects += comm_count
    
    # Institution projects
    for institution in Institution.objects.prefetch_related('projects').all():
        inst_count = institution.projects.count()
        institution_projects += inst_count

    # Researcher projects
    for researcher in Researcher.objects.prefetch_related('projects').all():
        res_count = researcher.projects.count()
        researcher_projects += res_count

    projects_count = Project.objects.count()

    # Labels
    bclabels_count = BCLabel.objects.count()
    tklabels_count = TKLabel.objects.count()
    total_labels = bclabels_count + tklabels_count

    current_datetime = datetime.datetime.now()

    context = {
        'community_count': community_count,
        'researcher_count': researcher_count,
        'institution_count': institution_count,
        'reg_total': reg_total,

        'bc_notice_count': bc_notice_count,
        'tk_notice_count': tk_notice_count,
        'notices_total': notices_total,

        'community_projects': community_projects,
        'institution_projects': institution_projects,
        'researcher_projects': researcher_projects,
        'projects_count': projects_count,

        'bclabels_count': bclabels_count,
        'tklabels_count': tklabels_count, 
        'total_labels': total_labels,
        'current_datetime': current_datetime,
    }
    
    return render(request, 'accounts/totals-count.html', context)
