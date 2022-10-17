import re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.contrib import messages
from django.core.paginator import Paginator
from itertools import chain

from django.contrib.auth.models import User
from accounts.models import UserAffiliation
from helpers.models import *
from notifications.models import *
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from projects.models import *

from helpers.forms import *
from bclabels.forms import *
from tklabels.forms import *
from projects.forms import *
from accounts.forms import ContactOrganizationForm

from localcontexts.utils import dev_prod_or_local
from bclabels.utils import check_bclabel_type
from tklabels.utils import check_tklabel_type
from projects.utils import *
from helpers.utils import *
from accounts.utils import get_users_name
from notifications.utils import *

from helpers.emails import *

from .forms import *
from .models import *

# pdfs
from django.http import HttpResponse, Http404
from django.template.loader import get_template
from xhtml2pdf import pisa

# Connect
@login_required(login_url='login')
def connect_community(request):
    community = True
    communities = Community.approved.all()
    form = JoinRequestForm(request.POST or None)

    if request.method == 'POST':
        community_name = request.POST.get('organization_name')
        if Community.objects.filter(community_name=community_name).exists():
            community = Community.objects.get(community_name=community_name)

            # If join request exists or user is already a member, display Error message
            request_exists = JoinRequest.objects.filter(user_from=request.user, community=community).exists()
            user_is_member = community.is_user_in_community(request.user)

            if request_exists or user_is_member:
                messages.add_message(request, messages.ERROR, "Either you have already sent this request or are currently a member of this community.")
                return redirect('connect-community')
            else:
                if form.is_valid():
                    data = form.save(commit=False)
                    data.user_from = request.user
                    data.community = community
                    data.user_to = community.community_creator
                    data.save()

                    # Send community creator email
                    send_join_request_email_admin(request, data, community)
                    messages.add_message(request, messages.SUCCESS, "Request to join community sent!")
                    return redirect('connect-community')
        else:
            messages.add_message(request, messages.ERROR, 'Community not in registry')
            return redirect('connect-community')

    context = { 'community': community, 'communities': communities, 'form': form,}
    return render(request, 'communities/connect-community.html', context)

@login_required(login_url='login')
def preparation_step(request):
    community = True
    return render(request, 'accounts/preparation.html', { 'community' : community })

# Create Community
@login_required(login_url='login')
def create_community(request):
    form = CreateCommunityForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.community_creator = request.user

            # If in test site, approve immediately, skip confirmation step
            if dev_prod_or_local(request.get_host()) == 'DEV':
                data.is_approved = True
                data.save()

                # Add to user affiliations
                affiliation = UserAffiliation.objects.prefetch_related('communities').get(user=request.user)
                affiliation.communities.add(data)
                affiliation.save()
                return redirect('dashboard')
            else:
                data.save()

                # Add to user affiliations
                affiliation = UserAffiliation.objects.prefetch_related('communities').get(user=request.user)
                affiliation.communities.add(data)
                affiliation.save()
                return redirect('confirm-community', data.id)
    return render(request, 'communities/create-community.html', {'form': form})

# Confirm Community
@login_required(login_url='login')
def confirm_community(request, community_id):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=community_id)

    form = ConfirmCommunityForm(request.POST or None, request.FILES, instance=community)
    if request.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.save()
            send_hub_admins_application_email(request, community, data)
            return redirect('dashboard')
    return render(request, 'accounts/confirm-account.html', {'form': form, 'community': community,})

def public_community_view(request, pk):
    try: 
        community = Community.objects.get(id=pk)
        bclabels = BCLabel.objects.filter(community=community, is_approved=True)
        tklabels = TKLabel.objects.filter(community=community, is_approved=True)
        created_projects = ProjectCreator.objects.filter(community=community)
        projects = []

        for p in created_projects:
            if p.project.project_privacy == 'Public':
                projects.append(p.project)

        if request.user.is_authenticated:
            user_communities = UserAffiliation.objects.prefetch_related('communities').get(user=request.user).communities.all()
            form = ContactOrganizationForm(request.POST or None)

            if request.method == 'POST':
                if 'contact_btn' in request.POST:
                    # contact community
                    if form.is_valid():
                        from_name = form.cleaned_data['name']
                        from_email = form.cleaned_data['email']
                        message = form.cleaned_data['message']
                        to_email = community.community_creator.email

                        send_contact_email(to_email, from_name, from_email, message)
                        messages.add_message(request, messages.SUCCESS, 'Message sent!')
                        return redirect('public-community', community.id)
                    else:
                        if not form.data['message']:
                            messages.add_message(request, messages.ERROR, 'Unable to send an empty message.')
                            return redirect('public-community', community.id)

                elif 'join_request' in request.POST:
                    # Request To Join community
                    if JoinRequest.objects.filter(user_from=request.user, community=community).exists():
                        messages.add_message(request, messages.ERROR, "You have already sent a request to this community")
                        return redirect('public-community', community.id)
                    else:
                        join_request = JoinRequest.objects.create(user_from=request.user, community=community, user_to=community.community_creator)
                        join_request.save()

                        # Send email to community creator
                        send_join_request_email_admin(request, join_request, community)
                        messages.add_message(request, messages.SUCCESS, 'Request sent!')
                        return redirect('public-community', community.id)
                else:
                    messages.add_message(request, messages.ERROR, 'Something went wrong')
                    return redirect('public-community', community.id)
        else:
            context = { 
                'community': community, 
                'bclabels' : bclabels,
                'tklabels' : tklabels,
                'projects' : projects,
            }
            return render(request, 'public.html', context)

        context = { 
            'community': community, 
            'bclabels' : bclabels,
            'tklabels' : tklabels,
            'projects' : projects,
            'form': form, 
            'user_communities': user_communities,
        }
        return render(request, 'public.html', context)
    except:
        raise Http404()


# Update Community / Settings
@login_required(login_url='login')
def update_community(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'editor' or member_role == 'viewer': # If user is not a member / does not have a role.
        return redirect('restricted')
    
    else:
        update_form = UpdateCommunityForm(instance=community)
        if member_role == 'admin': # Only admins can change the form 
            if request.method == "POST":
                update_form = UpdateCommunityForm(request.POST, request.FILES, instance=community)
                if update_form.is_valid():
                    update_form.save()
                    messages.add_message(request, messages.SUCCESS, 'Updated!')
                    return redirect('update-community', community.id)
            else:
                update_form = UpdateCommunityForm(instance=community)

        context = {
            'community': community,
            'update_form': update_form,
            'member_role': member_role,
        }
        return render(request, 'communities/update-community.html', context)

# Members
@login_required(login_url='login')
def community_members(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        # Get list of users, NOT in this community, alphabetized by name
        members = list(chain(
            community.admins.all().values_list('id', flat=True), 
            community.editors.all().values_list('id', flat=True), 
            community.viewers.all().values_list('id', flat=True),
        ))
        members.append(community.community_creator.id) # include community creator
        users = User.objects.exclude(id__in=members).order_by('username')

        join_requests_count = JoinRequest.objects.filter(community=community).count()
        form = InviteMemberForm(request.POST or None)

        if request.method == "POST":
            if 'change_member_role_btn' in request.POST:
                current_role = request.POST.get('current_role')
                new_role = request.POST.get('new_role')
                user_id = request.POST.get('user_id')
                member = User.objects.get(id=user_id)
                change_member_role(community, member, current_role, new_role)
                return redirect('members', community.id)

            elif 'send_invite_btn' in request.POST:
                selected_user = User.objects.none()
                if form.is_valid():
                    data = form.save(commit=False)

                    # Get target User
                    selected_username = request.POST.get('userList')
                    username_to_check = ''

                    if ' ' in selected_username: #if username includes spaces means it has a first and last name (last name,first name)
                        x = selected_username.split(' ')
                        username_to_check = x[0]
                    else:
                        username_to_check = selected_username

                    if not username_to_check in users.values_list('username', flat=True):
                        messages.add_message(request, messages.INFO, 'Invalid user selection. Please select user from the list.')
                    else:
                        selected_user = User.objects.get(username=username_to_check)

                        # Check to see if an invite or join request aleady exists
                        invitation_exists = InviteMember.objects.filter(receiver=selected_user, community=community).exists() # Check to see if invitation already exists
                        join_request_exists = JoinRequest.objects.filter(user_from=selected_user, community=community).exists() # Check to see if join request already exists

                        if not invitation_exists and not join_request_exists: # If invitation and join request does not exist, save form
                            data.receiver = selected_user
                            data.sender = request.user
                            data.status = 'sent'
                            data.community = community
                            data.save()
                            
                            send_community_invite_email(request, data, community) # Send email to target user
                            messages.add_message(request, messages.INFO, f'Invitation sent to {selected_user}')
                            return redirect('members', community.id)
                        else: 
                            messages.add_message(request, messages.INFO, f'The user you are trying to add already has an invitation pending to join {community.community_name}.')
                else:
                    messages.add_message(request, messages.INFO, 'Something went wrong')

        context = {
            'community': community,
            'member_role': member_role,
            'form': form,
            'join_requests_count': join_requests_count,
            'users': users,
        }
        return render(request, 'communities/members.html', context)

@login_required(login_url='login')
def member_requests(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        join_requests = JoinRequest.objects.filter(community=community)
        member_invites = InviteMember.objects.filter(community=community)

        if request.method == 'POST':
            selected_role = request.POST.get('selected_role')
            join_request_id = request.POST.get('join_request_id')

            accepted_join_request(community, join_request_id, selected_role)
            messages.add_message(request, messages.SUCCESS, 'You have successfully added a new member!')
            return redirect('member-requests', community.id)

        context = {
            'member_role': member_role,
            'community': community,
            'join_requests': join_requests,
            'member_invites': member_invites,
        }
        return render(request, 'communities/member-requests.html', context)

@login_required(login_url='login')
def delete_join_request(request, pk, join_id):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    join_request = JoinRequest.objects.get(id=join_id)
    join_request.delete()
    return redirect('member-requests', community.id)

@login_required(login_url='login')
def remove_member(request, pk, member_id):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    member = User.objects.get(id=member_id)
    # what role does member have
    # remove from role
    if member in community.admins.all():
        community.admins.remove(member)
    if member in community.editors.all():
        community.editors.remove(member)
    if member in community.viewers.all():
        community.viewers.remove(member)

    # remove community from userAffiliation instance
    affiliation = UserAffiliation.objects.get(user=member)
    affiliation.communities.remove(community)

    # Delete join request for this community if exists
    if JoinRequest.objects.filter(user_from=member, community=community).exists():
        join_request = JoinRequest.objects.get(user_from=member, community=community)
        join_request.delete()
    
    if '/manage/' in request.META.get('HTTP_REFERER'):
        return redirect('manage-orgs')
    else:
        return redirect('members', community.id)

# Select Labels to Customize
@login_required(login_url='login')
def select_label(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    bclabels = BCLabel.objects.select_related('created_by').prefetch_related('bclabel_translation', 'bclabel_note').filter(community=community)
    tklabels = TKLabel.objects.select_related('created_by').prefetch_related('tklabel_translation', 'tklabel_note').filter(community=community)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('public-community', community.id)
    else:
        if request.method == "POST":
            bclabel_code = request.POST.get('bc-label-code')
            tklabel_code = request.POST.get('tk-label-code')

            if bclabel_code:
                return redirect('customize-label', community.id, bclabel_code)

            if tklabel_code:
                return redirect('customize-label', community.id, tklabel_code)
        
        context = {
            'community': community,
            'member_role': member_role,
            'bclabels': bclabels,
            'tklabels': tklabels,
        }

        return render(request, 'communities/select-label.html', context)

@login_required(login_url='login')
def customize_label(request, pk, label_code):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer':
        return redirect('restricted')    
    else:
        label_type = ''
        form = ''
        title = ''
        name = get_users_name(request.user)

        if label_code.startswith('tk'):
            label_type = check_tklabel_type(label_code)
            form = CustomizeTKLabelForm(request.POST or None, request.FILES)
            title = f"A TK Label was customized by {name} and is waiting approval by another member of the community."

        elif label_code.startswith('bc'):
            label_type = check_bclabel_type(label_code)
            form = CustomizeBCLabelForm(request.POST or None, request.FILES)
            title = f"A BC Label was customized by {name} and is waiting approval by another member of the community."

        if request.method == "GET":
            add_translation_formset = AddLabelTranslationFormSet(queryset=LabelTranslation.objects.none())

        elif request.method == "POST":
            add_translation_formset = AddLabelTranslationFormSet(request.POST)

            if form.is_valid() and add_translation_formset.is_valid():
                data = form.save(commit=False)
                if not data.language:
                    data.language = 'English'
                data.label_type = label_type
                data.community = community
                data.created_by = request.user
                data.save()

                # Save all label translation instances
                instances = add_translation_formset.save(commit=False)
                for instance in instances:
                    if label_code.startswith('tk'):
                        instance.tklabel = data
                    elif label_code.startswith('bc'):
                        instance.bclabel = data
                    instance.save()
                
                # Create notification
                ActionNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title)
                return redirect('select-label', community.id)
            
        context = {
            'member_role': member_role,
            'community': community,
            'label_code': label_code,
            'form': form,
            'add_translation_formset': add_translation_formset,
        }
        return render(request, 'communities/customize-label.html', context)

@login_required(login_url='login')
def approve_label(request, pk, label_id):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer':
        return redirect('restricted')    
    else:
        # Init empty qs
        bclabel = BCLabel.objects.none()
        tklabel = TKLabel.objects.none()
        latest_approved_version = LabelVersion.objects.none()
        version_translations = LabelTranslationVersion.objects.none()

        if BCLabel.objects.filter(unique_id=label_id).exists():
            bclabel = BCLabel.objects.select_related('approved_by').get(unique_id=label_id)
            latest_approved_version = LabelVersion.objects.filter(bclabel=bclabel, is_approved=True).order_by('-version').first()

        if TKLabel.objects.filter(unique_id=label_id).exists():
            tklabel = TKLabel.objects.select_related('approved_by').get(unique_id=label_id)
            latest_approved_version = LabelVersion.objects.filter(tklabel=tklabel, is_approved=True).order_by('-version').first()
        
        version_translations = LabelTranslationVersion.objects.filter(version_instance=latest_approved_version)
        form = LabelNoteForm(request.POST or None)

        if request.method == 'POST':
            # If not approved, mark not approved and who it was by
            if 'create_label_note' in request.POST:
                if form.is_valid():
                    data = form.save(commit=False)
                    data.sender = request.user
                    if bclabel:
                        data.bclabel = bclabel
                        data.save()
                        bclabel.is_approved = False
                        bclabel.approved_by = request.user
                        bclabel.save()
                        send_email_label_approved(bclabel)
                    if tklabel:
                        data.tklabel = tklabel
                        data.save()
                        tklabel.is_approved = False
                        tklabel.approved_by = request.user
                        tklabel.save()
                        send_email_label_approved(tklabel)
                    return redirect('select-label', community.id)

            # If approved, save Label
            elif 'approve_label_yes' in request.POST:
                # BC LABEL
                if bclabel:
                    bclabel.is_approved = True
                    bclabel.approved_by = request.user
                    bclabel.save()
                    send_email_label_approved(bclabel)

                    # handle label versions and translation versions
                    handle_label_versions(bclabel)

                # TK LABEL
                if tklabel:
                    tklabel.is_approved = True
                    tklabel.approved_by = request.user
                    tklabel.save()
                    send_email_label_approved(tklabel)

                    # handle Label versions and translation versions
                    handle_label_versions(tklabel)

                return redirect('select-label', community.id)
        
        context = {
            'community': community,
            'member_role': member_role,
            'bclabel': bclabel,
            'tklabel': tklabel,
            'form': form,
            'latest_approved_version': latest_approved_version,
            'version_translations': version_translations,
        }
        return render(request, 'communities/approve-label.html', context)

# Edit Label before approval
@login_required(login_url='login')
def edit_label(request, pk, label_id):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    bclabel = BCLabel.objects.none()
    tklabel = TKLabel.objects.none()
    form = ''
    formset = ''

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer':
        return redirect('restricted')    
    else:

        add_translation_formset = AddLabelTranslationFormSet(request.POST or None)
        
        if request.method == 'GET':
            add_translation_formset = AddLabelTranslationFormSet(queryset=LabelTranslation.objects.none())

            if BCLabel.objects.filter(unique_id=label_id).exists():
                bclabel = BCLabel.objects.get(unique_id=label_id)
                form = EditBCLabelForm(instance=bclabel)
                formset = UpdateBCLabelTranslationFormSet(instance=bclabel)

            if TKLabel.objects.filter(unique_id=label_id).exists():
                tklabel = TKLabel.objects.get(unique_id=label_id)
                form = EditTKLabelForm(instance=tklabel)
                formset = UpdateTKLabelTranslationFormSet(instance=tklabel)

        elif request.method == 'POST':
            add_translation_formset = AddLabelTranslationFormSet(request.POST)

            if BCLabel.objects.filter(unique_id=label_id).exists():
                bclabel = BCLabel.objects.get(unique_id=label_id)
                form = EditBCLabelForm(request.POST, request.FILES, instance=bclabel)
                formset = UpdateBCLabelTranslationFormSet(request.POST or None, instance=bclabel)
                # Label goes back into the approval process
                if bclabel.is_approved:
                    bclabel.is_approved = False
                    bclabel.approved_by = None
                    bclabel.version += 1
                    bclabel.save()

            if TKLabel.objects.filter(unique_id=label_id).exists():
                tklabel = TKLabel.objects.get(unique_id=label_id)
                form = EditTKLabelForm(request.POST, request.FILES, instance=tklabel)
                formset = UpdateTKLabelTranslationFormSet(request.POST or None, instance=tklabel)
                 # Label goes back into the approval process
                if tklabel.is_approved:
                    tklabel.is_approved = False
                    tklabel.approved_by = None
                    tklabel.version += 1
                    tklabel.save()

            if form.is_valid() and formset.is_valid() and add_translation_formset.is_valid():
                form.save()
                formset.save()

                # Save all new label translation instances
                instances = add_translation_formset.save(commit=False)
                for instance in instances:
                    if BCLabel.objects.filter(unique_id=label_id).exists():
                        instance.bclabel = bclabel
                    elif TKLabel.objects.filter(unique_id=label_id).exists():
                        instance.tklabel = tklabel
                    
                    instance.save()

                return redirect('select-label', community.id)

        context = {
            'community': community,
            'member_role': member_role,
            'form': form,
            'formset': formset,
            'add_translation_formset': add_translation_formset,
            'bclabel': bclabel,
            'tklabel': tklabel,
        }
        return render(request, 'communities/edit-label.html', context)

@login_required(login_url='login')
def view_label(request, pk, label_uuid):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')    
    else:
        bclabel = BCLabel.objects.none()
        tklabel = TKLabel.objects.none()
        translations = LabelTranslation.objects.none()
        projects = Project.objects.none()
        creator_name = ''
        approver_name = ''
        bclabels = BCLabel.objects.none()
        tklabels = TKLabel.objects.none()
        label_versions = LabelVersion.objects.none()

        if BCLabel.objects.filter(unique_id=label_uuid).exists():
            bclabel = BCLabel.objects.select_related('created_by', 'approved_by').get(unique_id=label_uuid)
            translations = LabelTranslation.objects.filter(bclabel=bclabel)
            projects = bclabel.project_bclabels.all()
            creator_name = get_users_name(bclabel.created_by)
            approver_name = get_users_name(bclabel.approved_by)
            label_versions = LabelVersion.objects.filter(bclabel=bclabel).order_by('version')
            bclabels = BCLabel.objects.filter(community=community).exclude(unique_id=label_uuid).values('unique_id', 'name', 'label_type', 'is_approved')
            tklabels = TKLabel.objects.filter(community=community).values('unique_id', 'name', 'label_type', 'is_approved')
        if TKLabel.objects.filter(unique_id=label_uuid).exists():
            tklabel = TKLabel.objects.select_related('created_by', 'approved_by').get(unique_id=label_uuid)
            translations = LabelTranslation.objects.filter(tklabel=tklabel)
            projects = tklabel.project_tklabels.all()
            creator_name = get_users_name(tklabel.created_by)
            approver_name = get_users_name(tklabel.approved_by)
            label_versions = LabelVersion.objects.filter(tklabel=tklabel).order_by('version')
            tklabels = TKLabel.objects.filter(community=community).exclude(unique_id=label_uuid).values('unique_id', 'name', 'label_type', 'is_approved')
            bclabels = BCLabel.objects.filter(community=community).values('unique_id', 'name', 'label_type', 'is_approved')

        context = {
            'community': community,
            'member_role': member_role,
            'bclabels': bclabels,
            'tklabels': tklabels,
            'bclabel': bclabel,
            'tklabel': tklabel,
            'translations': translations,
            'projects': projects,
            'creator_name': creator_name,
            'approver_name': approver_name,
            'label_versions': label_versions,
        }

        return render(request, 'communities/view-label.html', context)


# Projects Main
@login_required(login_url='login')
def projects(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')    
    else:
        # 1. community projects + 
        # 2. projects community has been notified of 
        # 3. projects where community is contributor

        projects_list = list(chain(
            community.community_created_project.all().values_list('project__id', flat=True), 
            community.communities_notified.all().values_list('project__id', flat=True), 
            community.contributing_communities.all().values_list('project__id', flat=True),
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=project_ids).order_by('-date_added')

        p = Paginator(projects, 10)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)
        
        form = ProjectCommentForm(request.POST or None)

        # Form: Notify project contributor if project was seen
        if request.method == "POST":
            project_uuid = request.POST.get('project-uuid')
            project = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').get(unique_id=project_uuid)
            creator = ProjectCreator.objects.get(project=project) # get project creator

            if "notify-btn" in request.POST:
                if project_uuid != None and project_uuid != 'placeholder':
                    project_status = request.POST.get('project-status')
                    set_project_status(request.user, project, community, creator, project_status)                            
                    return redirect('community-projects', community.id)

            # Form: Add comment to notice
            elif "add-comment-btn" in request.POST:
                if form.is_valid():
                    if request.POST.get('message'):
                        data = form.save(commit=False)
                        data.project = project
                        data.sender = request.user
                        data.community = community
                        data.save()

                        project_status_seen_at_comment(request.user, community, creator, project)
                        return redirect('community-projects', community.id)
                    else:
                        return redirect('community-projects', community.id)
        elif request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
                query = SearchQuery(q)
                results = projects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        context = {
            'member_role': member_role,
            'projects': projects,
            'community': community,
            'form': form,
            'items': page,
            'results': results,
        }
        return render(request, 'communities/projects.html', context)

@login_required(login_url='login')
def projects_with_labels(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')    
    else:
        # init list for:
        # 1. community projects + 
        # 2. projects community has been notified of 
        # 3. projects where community is contributor
        projects_list = list(chain(
            community.community_created_project.all().values_list('project__id', flat=True), 
            community.communities_notified.all().values_list('project__id', flat=True), 
            community.contributing_communities.all().values_list('project__id', flat=True),
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids

        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=project_ids
            ).exclude(bc_labels=None).order_by('-date_added') | Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=project_ids
            ).exclude(tk_labels=None).order_by('-date_added')

        p = Paginator(projects, 10)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)
        
        form = ProjectCommentForm(request.POST or None)

        if request.method == "POST":
            project_uuid = request.POST.get('project-uuid')
            project = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').get(unique_id=project_uuid)
            creator = ProjectCreator.objects.get(project=project) # get project creator

            if "notify-btn" in request.POST:
                if project_uuid != None and project_uuid != 'placeholder':
                    project_status = request.POST.get('project-status')
                    set_project_status(request.user, project, community, creator, project_status)                                                        
                    return redirect('community-projects-labels', community.id)

            # Form: Add comment to notice
            elif "add-comment-btn" in request.POST:
                if form.is_valid():
                    if request.POST.get('message'):
                        data = form.save(commit=False)
                        data.project = project
                        data.sender = request.user
                        data.community = community
                        data.save()

                        project_status_seen_at_comment(request.user, community, creator, project)
                        return redirect('community-projects-labels', community.id)
                    else:
                        return redirect('community-projects-labels', community.id)
        elif request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
                query = SearchQuery(q)
                results = projects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        context = {
            'projects': projects,
            'community': community,
            'form': form,
            'member_role': member_role,
            'items': page,
            'results': results,
        }
        return render(request, 'communities/projects.html', context)

@login_required(login_url='login')
def projects_with_notices(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')    
    else:
        # init list for:
        # 1. community projects + 
        # 2. projects community has been notified of 
        # 3. projects where community is contributor
        projects_list = list(chain(
            community.community_created_project.all().values_list('project__id', flat=True), 
            community.communities_notified.all().values_list('project__id', flat=True), 
            community.contributing_communities.all().values_list('project__id', flat=True),
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=project_ids, tk_labels=None, bc_labels=None).order_by('-date_added')

        p = Paginator(projects, 10)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)
        
        form = ProjectCommentForm(request.POST or None)

        if request.method == "POST":
            project_uuid = request.POST.get('project-uuid')
            project = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').get(unique_id=project_uuid)
            creator = ProjectCreator.objects.get(project=project) # get project creator

            if "notify-btn" in request.POST:
                if project_uuid != None and project_uuid != 'placeholder':
                    project_status = request.POST.get('project-status')
                    set_project_status(request.user, project, community, creator, project_status)                            
                    return redirect('community-projects-notices', community.id)

            # Form: Add comment to notice
            elif "add-comment-btn" in request.POST:
                if form.is_valid():
                    if request.POST.get('message'):
                        data = form.save(commit=False)
                        data.project = project
                        data.sender = request.user
                        data.community = community
                        data.save()

                        project_status_seen_at_comment(request.user, community, creator, project)
                        return redirect('community-projects-notices', community.id)
                    else:
                        return redirect('community-projects-notices', community.id)
        elif request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
                query = SearchQuery(q)
                results = projects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        context = {
            'projects': projects,
            'community': community,
            'form': form,
            'member_role': member_role,
            'items': page,
            'results': results,
        }
        return render(request, 'communities/projects.html', context)

@login_required(login_url='login')
def projects_creator(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')    
    else:
        created_projects = community.community_created_project.all().values_list('project__id', flat=True)
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=created_projects).order_by('-date_added')

        p = Paginator(projects, 10)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)

        form = ProjectCommentForm(request.POST or None)

        if request.method == "POST":
            project_uuid = request.POST.get('project-uuid')
            project = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').get(unique_id=project_uuid)
            creator = ProjectCreator.objects.select_related('researcher', 'institution').get(project=project) # get project creator

            if "notify-btn" in request.POST:
                if project_uuid != None and project_uuid != 'placeholder':
                    project_status = request.POST.get('project-status')
                    set_project_status(request.user, project, community, creator, project_status)                                                        
                    return redirect('community-projects-creator', community.id)

            # Form: Add comment to notice
            elif "add-comment-btn" in request.POST:
                if form.is_valid():
                    if request.POST.get('message'):
                        data = form.save(commit=False)
                        data.project = project
                        data.sender = request.user
                        data.community = community
                        data.save()

                        project_status_seen_at_comment(request.user, community, creator, project)
                        return redirect('community-projects-creator', community.id)
                    else:
                        return redirect('community-projects-creator', community.id)
        elif request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
                query = SearchQuery(q)
                results = projects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        context = {
            'projects': projects,
            'community': community,
            'form': form,
            'member_role': member_role,
            'items': page,
            'results': results,
        }
        return render(request, 'communities/projects.html', context)

@login_required(login_url='login')
def projects_contributor(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')    
    else:
        # Get IDs of projects created by community and IDs of projects contributed, then exclude the created ones in the project call
        created_projects = community.community_created_project.all().values_list('project__id', flat=True)
        contrib = community.contributing_communities.all().values_list('project__id', flat=True)
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=contrib).exclude(id__in=created_projects).order_by('-date_added')

        p = Paginator(projects, 10)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)
        
        form = ProjectCommentForm(request.POST or None)

        if request.method == "POST":
            project_uuid = request.POST.get('project-uuid')
            project = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').get(unique_id=project_uuid)
            creator = ProjectCreator.objects.get(project=project) # get project creator

            if "notify-btn" in request.POST:
                if project_uuid != None and project_uuid != 'placeholder':
                    project_status = request.POST.get('project-status')
                    set_project_status(request.user, project, community, creator, project_status)                            
                    return redirect('community-projects-contributor', community.id)

            # Form: Add comment to notice
            elif "add-comment-btn" in request.POST:
                if form.is_valid():
                    if request.POST.get('message'):
                        data = form.save(commit=False)
                        data.project = project
                        data.sender = request.user
                        data.community = community
                        data.save()

                        project_status_seen_at_comment(request.user, community, creator, project)
                        return redirect('community-projects-contributor', community.id)
                    else:
                        return redirect('community-projects-contributor', community.id)
        elif request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
                query = SearchQuery(q)
                results = projects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        context = {
            'projects': projects,
            'community': community,
            'form': form,
            'member_role': member_role,
            'items': page,
            'results': results,
        }
        return render(request, 'communities/projects.html', context)


# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    community = Community.objects.select_related('community_creator').get(id=pk)

    bclabels = BCLabel.objects.filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.filter(community=community, is_approved=True)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return redirect('restricted')    
    else:
        if request.method == "GET":
            form = CreateProjectForm(request.GET or None)
            formset = ProjectPersonFormset(queryset=ProjectPerson.objects.none())
        elif request.method == 'POST':
            form = CreateProjectForm(request.POST)
            formset = ProjectPersonFormset(request.POST)

            if form.is_valid() and formset.is_valid():
                data = form.save(commit=False)
                data.project_creator = request.user

                # Define project_page field
                domain = request.get_host()
                if 'localhost' in domain:
                    data.project_page = f'http://{domain}/projects/{data.unique_id}'
                else:
                    data.project_page = f'https://{domain}/projects/{data.unique_id}'
                data.save()

                # Add project to community projects
                creator = ProjectCreator.objects.select_related('community').get(project=data)
                creator.community = community
                creator.save()

                # Get lists of contributors entered in form
                institutions_selected = request.POST.getlist('selected_institutions')
                researchers_selected = request.POST.getlist('selected_researchers')

                # Get a project contributor object and add community to it.
                contributors = ProjectContributors.objects.prefetch_related('communities').get(project=data)
                contributors.communities.add(community)

                # Add selected contributors to the ProjectContributors object
                add_to_contributors(request, contributors, institutions_selected, researchers_selected, data.unique_id)
                
                # Project person formset
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.project = data
                    instance.save()
                    # Send email to added person
                    send_project_person_email(request, instance.email, data.unique_id)

                # Send notification
                truncated_project_title = str(data.title)[0:30]
                name = get_users_name(data.project_creator)
                title = f'A new project was created by {name}: {truncated_project_title} ...'
                ActionNotification.objects.create(title=title, sender=request.user, community=community, notification_type='Projects', reference_id=data.unique_id)
                return redirect('community-projects', community.id)
        
        context = {
            'community': community,
            'member_role': member_role,
            'form': form,
            'formset': formset,
            'bclabels': bclabels,
            'tklabels': tklabels,
        }

        return render(request, 'communities/create-project.html', context)

@login_required(login_url='login')
def edit_project(request, community_id, project_uuid):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=community_id)
    project = Project.objects.prefetch_related('bc_labels', 'tk_labels').get(unique_id=project_uuid)
    
    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return redirect('restricted')    
    else:
        form = EditProjectForm(request.POST or None, instance=project)
        formset = ProjectPersonFormsetInline(request.POST or None, instance=project)
        contributors = ProjectContributors.objects.prefetch_related('institutions', 'researchers', 'communities').get(project=project)

        if request.method == 'POST':
            if form.is_valid() and formset.is_valid():
                data = form.save(commit=False)
                data.save()

                instances = formset.save(commit=False)
                for instance in instances:
                    instance.project = data
                    instance.save()

                # Get lists of contributors entered in form
                institutions_selected = request.POST.getlist('selected_institutions')
                researchers_selected = request.POST.getlist('selected_researchers')

                # Add selected contributors to the ProjectContributors object
                add_to_contributors(request, contributors, institutions_selected, researchers_selected, data.unique_id)
                return redirect('community-projects', community.id)

        context = {
            'member_role': member_role,
            'community': community, 
            'project': project, 
            'form': form,
            'formset': formset,
            'contributors': contributors,
        }
        return render(request, 'communities/edit-project.html', context)

@login_required(login_url='login')
def apply_labels(request, pk, project_uuid):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    project = Project.objects.prefetch_related('bc_labels', 'tk_labels').get(unique_id=project_uuid)
    project_creator = ProjectCreator.objects.get(project=project)
    bclabels = BCLabel.objects.select_related('community', 'created_by', 'approved_by').prefetch_related('bclabel_translation', 'bclabel_note').filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.select_related('community', 'created_by', 'approved_by').prefetch_related('tklabel_translation', 'tklabel_note').filter(community=community, is_approved=True)
    notices = project.project_notice.all()
    notes = ProjectNote.objects.filter(project=project)

    # Define Notification attrs
    reference_id = str(project.unique_id)
    truncated_project_title = str(project.title)[0:30]

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return redirect('restricted')    
    else:
        form = CreateProjectNoteForm(request.POST or None)

        if request.method == "POST":
            if form.data['note']:
                if form.is_valid():
                    data = form.save(commit=False)
                    data.community = community
                    data.project = project
                    data.save()

            # Set private project to discoverable
            if project.project_privacy == 'Private':
                project.project_privacy = 'Discoverable'
                project.save()

            # Get uuids of each label that was checked and add them to the project
            bclabels_selected = request.POST.getlist('selected_bclabels')
            tklabels_selected = request.POST.getlist('selected_tklabels')

            # if bc and tk labels are not null, clear
            if project.bc_labels.exists():
                project.bc_labels.clear()
            if project.tk_labels.exists():
                project.tk_labels.clear()

            # apply all selected labels
            for bclabel_uuid in bclabels_selected:
                bclabel = BCLabel.objects.get(unique_id=bclabel_uuid)
                project.bc_labels.add(bclabel)

            for tklabel_uuid in tklabels_selected:
                tklabel = TKLabel.objects.get(unique_id=tklabel_uuid)
                project.tk_labels.add(tklabel)
            
            project.save()
            
            if notices:
                # add community to project contributors
                contributors = ProjectContributors.objects.get(project=project)
                contributors.communities.add(community)
                contributors.save()

                # Archive Notices
                for notice in notices:
                    notice.archived = True
                    notice.save()
                
                #reset status
                status = ProjectStatus.objects.get(project=project, community=community)
                status.seen = True
                status.status = 'labels_applied'
                status.save()
            else:
                comm_title = 'Labels have been applied to the project ' + truncated_project_title + ' ...'
                ActionNotification.objects.create(title=comm_title, notification_type='Projects', community=community, reference_id=reference_id)

            # send email to project creator
            send_email_labels_applied(project, community)
            messages.add_message(request, messages.SUCCESS, "Labels applied!")
            return redirect('apply-labels', community.id, project.unique_id)

    context = {
        'member_role': member_role,
        'community': community,
        'project': project,
        'project_creator': project_creator,
        'bclabels': bclabels,
        'tklabels': tklabels,
        'notes': notes,
        'form': form,
    }
    return render(request, 'communities/apply-labels.html', context)

@login_required(login_url='login')
def connections(request, pk):
    community = Community.objects.select_related('community_creator').get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')    
    else:
        institution_ids = list(chain(
            community.contributing_communities.exclude(institutions__id=None).values_list('institutions__id', flat=True),
        ))

        researcher_ids = list(chain(
            community.contributing_communities.exclude(researchers__id=None).values_list('researchers__id', flat=True),
        ))

        institutions = Institution.objects.select_related('institution_creator').filter(id__in=institution_ids)
        researchers = Researcher.objects.select_related('user').filter(id__in=researcher_ids)

        context = {
            'member_role': member_role,
            'community': community,
            'researchers': researchers,
            'institutions': institutions
        }
        return render(request, 'communities/connections.html', context)
        
# show community Labels in a PDF
@login_required(login_url='login')
def labels_pdf(request, pk):
    # Get approved labels customized by community
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    bclabels = BCLabel.objects.filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.filter(community=community, is_approved=True)

    template_path = 'snippets/pdfs/community-labels.html'
    context = {'community': community, 'bclabels': bclabels, 'tklabels': tklabels,}

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')

    # if download:
    # response['Content-Disposition'] = 'attachment; filename="labels.pdf"'
    
    # if display
    response['Content-Disposition'] = 'filename="labels.pdf"'

    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required(login_url='login')
def download_labels(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    bclabels = BCLabel.objects.filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.filter(community=community, is_approved=True)

    template_path = 'snippets/pdfs/community-labels.html'
    context = {'community': community, 'bclabels': bclabels, 'tklabels': tklabels,}

    files = []

    # Add PDF to zip
    pdf = render_to_pdf(template_path, context)
    files.append(('Labels_Overview.pdf', pdf))

    # Labels Usage guide PDF
    usage_guide_url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-TK_BC-Labels-Usage-Guide_2021-11-02.pdf'
    response = requests.get(usage_guide_url) 
    files.append(('BC_TK_Label_Usage_Guide.pdf', response.content))

    # Add Label images, text and translations
    for bclabel in bclabels:
        get_image = requests.get(bclabel.img_url)
        get_svg = requests.get(bclabel.svg_url)
        files.append((bclabel.name + '.png', get_image.content))
        files.append((bclabel.name + '.svg', get_svg.content))

        # Default Label text
        text_content = bclabel.name + '\n' + bclabel.label_text
        text_addon = []

        if bclabel.bclabel_translation.all():
            for translation in bclabel.bclabel_translation.all():
                text_addon.append('\n\n' + translation.translated_name + ' (' + translation.language + ') ' + '\n' + translation.translated_text)
            files.append((bclabel.name + '.txt', text_content + '\n'.join(text_addon)))
        else:
            files.append((bclabel.name + '.txt', text_content))

    # Add Label images, text and translations
    for tklabel in tklabels:
        get_image = requests.get(tklabel.img_url)
        get_svg = requests.get(tklabel.svg_url)
        files.append((tklabel.name + '.png', get_image.content))
        files.append((tklabel.name + '.svg', get_svg.content))
        
        # Default Label text
        text_content = tklabel.name + '\n' + tklabel.label_text
        text_addon = []

        if tklabel.tklabel_translation.all():
            for translation in tklabel.tklabel_translation.all():
                text_addon.append('\n\n' + translation.translated_name + ' (' + translation.language + ') ' + '\n' + translation.translated_text)
            files.append((tklabel.name + '.txt', text_content + '\n'.join(text_addon)))
        else:
            files.append((tklabel.name + '.txt', text_content))
    
    # Create Readme
    readme_text = "The Traditional Knowledge (TK) and Biocultural (BC) Labels reinforce the cultural authority and rights of Indigenous communities.\nThe TK and BC Labels are intended to be displayed prominently on public-facing Indigenous community, researcher and institutional websites, metadata and digital collection's pages.\n\nThis folder contains the following files:\n"
    file_names = []
    for f in files:
        file_names.append(f[0])
    readme_content = readme_text + '\n'.join(file_names) + '\n\nRefer to the Usage Guide for details on how to adapt and display the Labels for your community.\n\nFor more information, contact Local Contexts at localcontexts.org or support@localcontexts.org'
    files.append(('README.txt', readme_content))

    # Generate zip file 
    full_zip_in_memory = generate_zip(files)

    response = HttpResponse(full_zip_in_memory, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(community.community_name + '-Labels.zip')

    return response