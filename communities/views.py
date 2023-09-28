from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
from accounts.forms import ContactOrganizationForm, SignUpInvitationForm

from localcontexts.utils import dev_prod_or_local
from projects.utils import *
from helpers.utils import *
from accounts.utils import get_users_name
from notifications.utils import *
from helpers.downloads import download_labels_zip
from helpers.emails import *

from .forms import *
from .models import *
from .decorators import member_required
from .utils import *

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

                    send_action_notification_join_request(data) # Send action notification to community
                    send_join_request_email_admin(request, data, community) # Send community creator email
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

                # Adds activity to Hub Activity
                HubActivity.objects.create(
                    action_user_id=request.user.id,
                    action_type="New Community",
                    community_id=data.id,
                    action_account_type='community'
                )
                return redirect('confirm-community', data.id)
    return render(request, 'communities/create-community.html', {'form': form})

# Confirm Community
@login_required(login_url='login')
def confirm_community(request, community_id):
    community = Community.objects.select_related('community_creator').get(id=community_id)

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
                
        projects_list = list(chain(
            community.community_created_project.all().values_list('project__unique_id', flat=True), # community created project ids
            community.tklabel_community.all().values_list('project_tklabels__unique_id', flat=True), # projects where tk labels have been applied
            community.bclabel_community.all().values_list('project_bclabels__unique_id', flat=True), # projects where bclabels have been applied
            community.contributing_communities.all().values_list('project__unique_id', flat=True), # projects where community is contributor
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        archived = ProjectArchived.objects.filter(project_uuid__in=project_ids, community_id=community.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        projects = Project.objects.select_related('project_creator').filter(unique_id__in=project_ids, project_privacy='Public').exclude(unique_id__in=archived).order_by('-date_modified')

        if request.user.is_authenticated:
            user_communities = UserAffiliation.objects.prefetch_related('communities').get(user=request.user).communities.all()
            form = ContactOrganizationForm(request.POST or None)
            join_form = JoinRequestForm(request.POST or None)

            if request.method == 'POST':
                if 'contact_btn' in request.POST:
                    # contact community
                    if form.is_valid():
                        from_name = form.cleaned_data['name']
                        from_email = form.cleaned_data['email']
                        message = form.cleaned_data['message']
                        to_email = community.community_creator.email

                        send_contact_email(to_email, from_name, from_email, message, community)
                        messages.add_message(request, messages.SUCCESS, 'Message sent!')
                        return redirect('public-community', community.id)
                    else:
                        if not form.data['message']:
                            messages.add_message(request, messages.ERROR, 'Unable to send an empty message.')
                            return redirect('public-community', community.id)

                elif 'join_request' in request.POST:
                    if join_form.is_valid():
                        data = join_form.save(commit=False)

                        # Request To Join community
                        if JoinRequest.objects.filter(user_from=request.user, community=community).exists():
                            messages.add_message(request, messages.ERROR, "You have already sent a request to this community")
                            return redirect('public-community', community.id)
                        else:
                            data.user_from = request.user
                            data.community = community
                            data.user_to = community.community_creator
                            data.save()

                            send_action_notification_join_request(data) # Send action notiication to community
                            send_join_request_email_admin(request, data, community) # Send email to community creator
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
            'join_form': join_form,
            'user_communities': user_communities,
        }
        return render(request, 'public.html', context)
    except:
        raise Http404()


# Update Community / Settings
@login_required(login_url='login')
@member_required(roles=['admin'])
def update_community(request, pk):
    community = get_community(pk)
    member_role = check_member_role(request.user, community)
    update_form = UpdateCommunityForm(instance=community)

    if request.method == "POST":
        update_form = UpdateCommunityForm(request.POST, request.FILES, instance=community)
        
        if 'clear_image' in request.POST:
            community.image = None
            community.save()
            return redirect('update-community', community.id)
        else:
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
@member_required(roles=['admin', 'editor', 'viewer'])
def community_members(request, pk):
    community = get_community(pk)
    member_role = check_member_role(request.user, community)

    # Get list of users in this community, alphabetized by name
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
                        
                        send_account_member_invite(data) # Send action notification
                        send_member_invite_email(request, data, community) # Send email to target user
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
        'invite_form': SignUpInvitationForm()
    }
    return render(request, 'communities/members.html', context)

@login_required(login_url='login')
@member_required(roles=['admin', 'editor', 'viewer'])
def member_requests(request, pk):
    community = get_community(pk)
    member_role = check_member_role(request.user, community)
    join_requests = JoinRequest.objects.filter(community=community)
    member_invites = InviteMember.objects.filter(community=community)

    if request.method == 'POST':
        selected_role = request.POST.get('selected_role')
        join_request_id = request.POST.get('join_request_id')

        accepted_join_request(request, community, join_request_id, selected_role)
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
@member_required(roles=['admin'])
def delete_join_request(request, pk, join_id):
    community = get_community(pk)
    join_request = JoinRequest.objects.get(id=join_id)
    join_request.delete()
    return redirect('member-requests', community.id)

@login_required(login_url='login')
@member_required(roles=['admin'])
def remove_member(request, pk, member_id):
    community = get_community(pk)
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
    
    title = f'You have been removed as a member from {community.community_name}.'
    UserNotification.objects.create(from_user=request.user, to_user=member, title=title, notification_type="Remove", community=community)

    if '/manage/' in request.META.get('HTTP_REFERER'):
        return redirect('manage-orgs')
    else:
        return redirect('members', community.id)

# Select Labels to Customize
@login_required(login_url='login')
@member_required(roles=['admin', 'editor', 'viewer'])
def select_label(request, pk):
    community = get_community(pk)
    bclabels = BCLabel.objects.select_related('created_by').prefetch_related('bclabel_translation', 'bclabel_note').filter(community=community)
    tklabels = TKLabel.objects.select_related('created_by').prefetch_related('tklabel_translation', 'tklabel_note').filter(community=community)

    member_role = check_member_role(request.user, community)
    can_download = community.is_approved and dev_prod_or_local(request.get_host()) != 'DEV'
    is_sandbox = dev_prod_or_local(request.get_host()) == 'DEV'

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
        'can_download': can_download,
        'is_sandbox': is_sandbox,
    }

    return render(request, 'communities/select-label.html', context)

@login_required(login_url='login')
@member_required(roles=['admin', 'editor'])
def customize_label(request, pk, label_code):
    community = get_community(pk)
    member_role = check_member_role(request.user, community)
    name = get_users_name(request.user)

    if does_label_type_exist(community, label_code): # check if label of this type already exists
        messages.error(request, 'A Label of this type has already been customized by your community')
        return redirect('select-label', community.id)
    else:
        form_class, label_display, label_type = get_form_and_label_type(label_code)
        form = form_class(request.POST or None, request.FILES)
        title = f"A {label_display} was customized by {name} and is waiting approval by another member of the community."

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
                ActionNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title, reference_id=data.unique_id)
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
@member_required(roles=['admin', 'editor'])
def approve_label(request, pk, label_id):
    community = get_community(pk)
    member_role = check_member_role(request.user, community)

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

                    send_action_notification_label_approved(bclabel)
                    send_email_label_approved(request, bclabel, data.id)

                if tklabel:
                    data.tklabel = tklabel
                    data.save()
                    tklabel.is_approved = False
                    tklabel.approved_by = request.user
                    tklabel.save()

                    send_action_notification_label_approved(tklabel)
                    send_email_label_approved(request, tklabel, data.id)
                return redirect('select-label', community.id)

        # If approved, save Label
        elif 'approve_label_yes' in request.POST:
            # BC LABEL
            if bclabel:
                bclabel.is_approved = True
                bclabel.approved_by = request.user
                bclabel.save()

                handle_label_versions(bclabel) # handle Label versions and translation versions

                send_action_notification_label_approved(bclabel)
                send_email_label_approved(request, bclabel, None)

            # TK LABEL
            if tklabel:
                tklabel.is_approved = True
                tklabel.approved_by = request.user
                tklabel.save()

                handle_label_versions(tklabel) # handle Label versions and translation versions

                send_action_notification_label_approved(tklabel)
                send_email_label_approved(request, tklabel, None)

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
@member_required(roles=['admin', 'editor'])
def edit_label(request, pk, label_id):
    community = get_community(pk)
    bclabel = BCLabel.objects.none()
    tklabel = TKLabel.objects.none()
    form = ''
    formset = ''
    member_role = check_member_role(request.user, community)
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
                bclabel.last_edited_by = request.user
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
                tklabel.last_edited_by = request.user
                tklabel.version += 1
                tklabel.save()

        if 'clear_audiofile' in request.POST:
            if bclabel:
                bclabel.audiofile = None
                bclabel.save()
                return redirect('edit-label', community.id, bclabel.unique_id)
            elif tklabel:
                tklabel.audiofile = None
                tklabel.save()                
                return redirect('edit-label', community.id, tklabel.unique_id)
            else:
                pass
        else:
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
@member_required(roles=['admin', 'editor', 'viewer'])
def view_label(request, pk, label_uuid):
    community = get_community(pk)
    member_role = check_member_role(request.user, community)
    bclabel = BCLabel.objects.none()
    tklabel = TKLabel.objects.none()
    projects = Project.objects.none()
    creator_name = ''
    approver_name = ''
    bclabels = BCLabel.objects.none()
    tklabels = TKLabel.objects.none()
    label_versions = LabelVersion.objects.none()

    if BCLabel.objects.filter(unique_id=label_uuid).exists():
        bclabel = BCLabel.objects.select_related('created_by', 'approved_by').get(unique_id=label_uuid)
        projects = bclabel.project_bclabels.all()
        creator_name = get_users_name(bclabel.created_by)
        approver_name = get_users_name(bclabel.approved_by)
        last_editor_name = get_users_name(bclabel.last_edited_by)
        label_versions = LabelVersion.objects.filter(bclabel=bclabel).order_by('version')
        bclabels = BCLabel.objects.filter(community=community).exclude(unique_id=label_uuid).values('unique_id', 'name', 'label_type', 'is_approved')
        tklabels = TKLabel.objects.filter(community=community).values('unique_id', 'name', 'label_type', 'is_approved')
    if TKLabel.objects.filter(unique_id=label_uuid).exists():
        tklabel = TKLabel.objects.select_related('created_by', 'approved_by').get(unique_id=label_uuid)
        projects = tklabel.project_tklabels.all()
        creator_name = get_users_name(tklabel.created_by)
        approver_name = get_users_name(tklabel.approved_by)
        last_editor_name = get_users_name(tklabel.last_edited_by)
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
        'projects': projects,
        'creator_name': creator_name,
        'approver_name': approver_name,
        'last_editor_name': last_editor_name,
        'label_versions': label_versions,
    }

    return render(request, 'communities/view-label.html', context)


# Projects Main
@login_required(login_url='login')
@member_required(roles=['admin', 'editor', 'viewer'])
def projects(request, pk):
    community = get_community(pk)
    member_role = check_member_role(request.user, community)

    bool_dict = {
        'has_labels': False,
        'has_notices': False,
        'created': False,
        'contributed': False,
        'is_archived': False,
        'title_az': False,
        'visibility_public': False,
        'visibility_contributor': False,
        'visibility_private': False,
        'date_modified': False
    }

    projects_list = list(chain(
        community.community_created_project.all().values_list('project__unique_id', flat=True), # community created project ids
        community.communities_notified.all().values_list('project__unique_id', flat=True), # projects community has been notified of
        community.contributing_communities.all().values_list('project__unique_id', flat=True), # projects where community is contributor
    ))
    project_ids = list(set(projects_list)) # remove duplicate ids
    archived = ProjectArchived.objects.filter(project_uuid__in=project_ids, community_id=community.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
    projects = Project.objects.select_related('project_creator').filter(unique_id__in=project_ids).exclude(unique_id__in=archived).order_by('-date_added')

    sort_by = request.GET.get('sort')

    if sort_by == 'all':
        return redirect('community-projects', community.id)
    
    elif sort_by == 'has_labels':
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids
            ).exclude(unique_id__in=archived).exclude(bc_labels=None).order_by('-date_added') | Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids
            ).exclude(unique_id__in=archived).exclude(tk_labels=None).order_by('-date_added')
        bool_dict['has_labels'] = True
    
    elif sort_by == 'has_notices':
        # FIXME: This should exclude community created projects?
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids, tk_labels=None, bc_labels=None).exclude(unique_id__in=archived).order_by('-date_added')
        bool_dict['has_notices'] = True

    elif sort_by == 'created':
        created_projects = community.community_created_project.all().values_list('project__unique_id', flat=True)
        archived = ProjectArchived.objects.filter(project_uuid__in=created_projects, community_id=community.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=created_projects).exclude(unique_id__in=archived).order_by('-date_added')
        bool_dict['created'] = True

    elif sort_by == 'contributed':
        contrib = community.contributing_communities.all().values_list('project__unique_id', flat=True) # get uuids of contributed projects
        projects_list = list(chain(
            community.community_created_project.all().values_list('project__unique_id', flat=True), # check community created projects
            ProjectArchived.objects.filter(project_uuid__in=contrib, community_id=community.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=contrib).exclude(unique_id__in=project_ids).order_by('-date_added')
        bool_dict['contributed'] = True

    elif sort_by == 'archived':
        archived_projects = ProjectArchived.objects.filter(community_id=community.id, archived=True).values_list('project_uuid', flat=True)
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=archived_projects).order_by('-date_added')
        bool_dict['is_archived'] = True

    elif sort_by == 'title_az':
        projects = projects.order_by('title')
        bool_dict['title_az'] = True

    elif sort_by == 'visibility_public':
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids, project_privacy='Public').exclude(unique_id__in=archived).order_by('-date_added')
        bool_dict['visibility_public'] = True

    elif sort_by == 'visibility_contributor':
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids, project_privacy='Contributor').exclude(unique_id__in=archived).order_by('-date_added')
        bool_dict['visibility_contributor'] = True

    elif sort_by == 'visibility_private':
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids, project_privacy='Private').exclude(unique_id__in=archived).order_by('-date_added')
        bool_dict['visibility_private'] = True

    elif sort_by == 'date_modified':
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids).exclude(unique_id__in=archived).order_by('-date_modified')
        bool_dict['date_modified'] = True

    page = paginate(request, projects, 10)

    if request.method == 'GET':
        results = return_project_search_results(request, projects)

    context = {
        'member_role': member_role,
        'projects': projects,
        'community': community,
        'items': page,
        'results': results,
        'bool_dict': bool_dict,
    }
    return render(request, 'communities/projects.html', context)


# Create Project
@login_required(login_url='login')
@member_required(roles=['admin', 'editor'])
def create_project(request, pk, source_proj_uuid=None, related=None):
    community = get_community(pk)
    creator_name = get_users_name(request.user)

    member_role = check_member_role(request.user, community)
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
            data.project_page = f'{request.scheme}://{request.get_host()}/projects/{data.unique_id}'
            
            # Handle multiple urls, save as array
            project_links = request.POST.getlist('project_urls')
            data.urls = project_links

            data.save()

            if source_proj_uuid and not related:
                data.source_project_uuid = source_proj_uuid
                data.save()
                ProjectActivity.objects.create(project=data, activity=f'Sub Project "{data.title}" was added to Project by {creator_name} | {community.community_name}')

            if source_proj_uuid and related:
                source = Project.objects.get(unique_id=source_proj_uuid)
                data.related_projects.add(source)
                source.related_projects.add(data)
                source.save()
                data.save()
                
                ProjectActivity.objects.create(project=data, activity=f'Project "{source.title}" was connected to Project by {creator_name} | {community.community_name}')
                ProjectActivity.objects.create(project=source, activity=f'Project "{data.title}" was connected to Project by {creator_name} | {community.community_name}')

            # Create Activity
            ProjectActivity.objects.create(project=data, activity=f'Project was created by {creator_name} | {community.community_name}')

            # Adds activity to Hub Activity
            HubActivity.objects.create(
                action_user_id=request.user.id,
                action_type="Project Created",
                project_id=data.id,
                action_account_type = 'community',
                community_id=community.id
            )

            # Add project to community projects
            creator = ProjectCreator.objects.select_related('community').get(project=data)
            creator.community = community
            creator.save()

            # Add selected contributors to the ProjectContributors object
            add_to_contributors(request, community, data)
            
            # Project person formset
            instances = formset.save(commit=False)
            for instance in instances:
                if instance.name or instance.email:
                    instance.project = data
                    instance.save()
                # Send email to added person
                send_project_person_email(request, instance.email, data.unique_id, community)

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
    }

    return render(request, 'communities/create-project.html', context)

@login_required(login_url='login')
@member_required(roles=['admin', 'editor'])
def edit_project(request, pk, project_uuid):
    community = get_community(pk)
    project = Project.objects.prefetch_related('bc_labels', 'tk_labels').get(unique_id=project_uuid)
    member_role = check_member_role(request.user, community)

    form = EditProjectForm(request.POST or None, instance=project)
    formset = ProjectPersonFormsetInline(request.POST or None, instance=project)
    contributors = ProjectContributors.objects.prefetch_related('institutions', 'researchers', 'communities').get(project=project)

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            data = form.save(commit=False)
            project_links = request.POST.getlist('project_urls')
            data.urls = project_links
            data.save()

            editor_name = get_users_name(request.user)
            ProjectActivity.objects.create(project=data, activity=f'Edits to Project were made by {editor_name}')

            # Adds activity to Hub Activity
            HubActivity.objects.create(
                action_user_id=request.user.id,
                action_type="Project Edited",
                project_id=data.id,
                action_account_type = 'community',
                community_id=pk
            )

            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.name or not instance.email:
                    instance.delete()
                else:
                    instance.project = data
                    instance.save()

            # Add selected contributors to the ProjectContributors object
            add_to_contributors(request, community, data)
            return redirect('community-project-actions', community.id, project.unique_id)

    context = {
        'member_role': member_role,
        'community': community, 
        'project': project, 
        'form': form,
        'formset': formset,
        'contributors': contributors,
        'urls': project.urls,
    }
    return render(request, 'communities/edit-project.html', context)

def project_actions(request, pk, project_uuid):
    try:
        community = get_community(pk)
        project = Project.objects.prefetch_related(
                'bc_labels', 
                'tk_labels', 
                'bc_labels__community', 
                'tk_labels__community',
                'bc_labels__bclabel_translation', 
                'tk_labels__tklabel_translation',
                ).get(unique_id=project_uuid)

        member_role = check_member_role(request.user, community)
        if not member_role or not request.user.is_authenticated or not project.can_user_access(request.user):
            return redirect('view-project', project_uuid)    
        else:
            notices = Notice.objects.filter(project=project, archived=False)
            creator = ProjectCreator.objects.get(project=project)
            current_status = ProjectStatus.objects.filter(project=project, community=community).first()
            statuses = ProjectStatus.objects.filter(project=project)
            comments = ProjectComment.objects.select_related('sender').filter(project=project)
            activities = ProjectActivity.objects.filter(project=project).order_by('-date')
            is_community_notified = EntitiesNotified.objects.none()
            sub_projects = Project.objects.filter(source_project_uuid=project.unique_id).values_list('unique_id', 'title')
            name = get_users_name(request.user)
            label_groups = return_project_labels_by_community(project)
            can_download = can_download_project(request, creator)

            # for related projects list 
            project_ids = list(set(community.community_created_project.all().values_list('project__unique_id', flat=True)
                .union(community.communities_notified.all().values_list('project__unique_id', flat=True))
                .union(community.contributing_communities.all().values_list('project__unique_id', flat=True))))
            project_ids_to_exclude_list = list(project.related_projects.all().values_list('unique_id', flat=True)) #projects that are currently related
            project_ids = list(set(project_ids).difference(project_ids_to_exclude_list)) # exclude projects that are already related
            projects_to_link = Project.objects.filter(unique_id__in=project_ids).exclude(unique_id=project.unique_id).order_by('-date_added').values_list('unique_id', 'title')

            if not creator.community:
            # 1. is community creator of project?
            # 2. if no, has community been notified?
                is_community_notified = EntitiesNotified.objects.filter(communities=community, project=project).exists()


            project_archived = False
            if ProjectArchived.objects.filter(project_uuid=project.unique_id, community_id=community.id).exists():
                x = ProjectArchived.objects.get(project_uuid=project.unique_id, community_id=community.id)
                project_archived = x.archived

            form = ProjectCommentForm(request.POST or None)

            if request.method == "POST":
                if 'add-comment-btn' in request.POST:
                    if form.is_valid():
                        if request.POST.get('message'):
                            data = form.save(commit=False)
                            data.project = project
                            data.sender = request.user
                            data.sender_affiliation = community.community_name
                            data.save()
                            project_status_seen_at_comment(request.user, community, creator, project)
                            # send notification to contributors

                            send_action_notification_to_project_contribs(project)
                            return redirect('community-project-actions', community.id, project.unique_id)
                        else:
                            return redirect('community-project-actions', community.id, project.unique_id)
                        
                elif "notify-btn" in request.POST:
                    project_status = request.POST.get('project-status')
                    set_project_status(request.user, project, community, creator, project_status)                            
                    return redirect('community-project-actions', community.id, project.unique_id)
                
                elif 'link_projects_btn' in request.POST:
                    selected_projects = request.POST.getlist('projects_to_link')

                    activities = []
                    for uuid in selected_projects:
                        project_to_add = Project.objects.get(unique_id=uuid)
                        project.related_projects.add(project_to_add)
                        project_to_add.related_projects.add(project)
                        project_to_add.save()

                        activities.append(ProjectActivity(project=project, activity=f'Project "{project_to_add.title}" was connected to Project by {name} | {community.community_name}'))
                        activities.append(ProjectActivity(project=project_to_add, activity=f'Project "{project.title}" was connected to Project by {name} | {community.community_name}'))
                                
                    ProjectActivity.objects.bulk_create(activities)
                    project.save()
                    return redirect('community-project-actions', community.id, project.unique_id)
                
                elif 'delete_project' in request.POST:
                    return redirect('community-delete-project', community.id, project.unique_id)
                
                elif 'remove_contributor' in request.POST:
                    contribs = ProjectContributors.objects.get(project=project)
                    contribs.communities.remove(community)
                    contribs.save()
                    return redirect('community-project-actions', community.id, project.unique_id)

            context = {
                'member_role': member_role,
                'community': community,
                'project': project,
                'notices': notices,
                'creator': creator,
                'form': form,
                'current_status': current_status,
                'statuses': statuses,
                'comments': comments,
                'activities': activities,
                'project_archived': project_archived,
                'is_community_notified': is_community_notified,
                'sub_projects': sub_projects,
                'projects_to_link': projects_to_link,
                'label_groups': label_groups,
                'can_download': can_download,
            }
            return render(request, 'communities/project-actions.html', context)
    except:
        raise Http404()

@login_required(login_url='login')
@member_required(roles=['admin', 'editor'])
def archive_project(request, pk, project_uuid):
    if not ProjectArchived.objects.filter(community_id=pk, project_uuid=project_uuid).exists():
        ProjectArchived.objects.create(community_id=pk, project_uuid=project_uuid, archived=True)
    else:
        archived_project = ProjectArchived.objects.get(community_id=pk, project_uuid=project_uuid)
        if archived_project.archived:
            archived_project.archived = False
        else:
            archived_project.archived = True
        archived_project.save()
    return redirect('community-project-actions', pk, project_uuid)

@login_required(login_url='login')
@member_required(roles=['admin', 'editor'])
def delete_project(request, pk, project_uuid):
    community = Community.objects.get(id=pk)
    project = Project.objects.get(unique_id=project_uuid)

    if ActionNotification.objects.filter(reference_id=project.unique_id).exists():
        for notification in ActionNotification.objects.filter(reference_id=project.unique_id):
            notification.delete()
    
    project.delete()
    return redirect('community-projects', community.id)

@login_required(login_url='login')
@member_required(roles=['admin', 'editor'])
def unlink_project(request, pk, target_proj_uuid, proj_to_remove_uuid):
    community = Community.objects.get(id=pk)
    target_project = Project.objects.get(unique_id=target_proj_uuid)
    project_to_remove = Project.objects.get(unique_id=proj_to_remove_uuid)
    target_project.related_projects.remove(project_to_remove)
    project_to_remove.related_projects.remove(target_project)
    target_project.save()
    project_to_remove.save()
    name = get_users_name(request.user)
    ProjectActivity.objects.create(project=project_to_remove, activity=f'Connection was removed between Project "{project_to_remove}" and Project "{target_project}" by {name}')
    ProjectActivity.objects.create(project=target_project, activity=f'Connection was removed between Project "{target_project}" and Project "{project_to_remove}" by {name}')
    return redirect('community-project-actions', community.id, target_project.unique_id)

@login_required(login_url='login')
@member_required(roles=['admin', 'editor'])
def apply_labels(request, pk, project_uuid):
    community = get_community(pk)
    project = Project.objects.prefetch_related('bc_labels', 'tk_labels').get(unique_id=project_uuid)
    creator = ProjectCreator.objects.get(project=project)
    bclabels = BCLabel.objects.select_related('community', 'created_by', 'approved_by').prefetch_related('bclabel_translation', 'bclabel_note').filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.select_related('community', 'created_by', 'approved_by').prefetch_related('tklabel_translation', 'tklabel_note').filter(community=community, is_approved=True)
    notices = project.project_notice.all()
    notes = ProjectNote.objects.filter(project=project)

    # Define Notification attrs
    reference_id = str(project.unique_id)
    truncated_project_title = str(project.title)[0:30]

    member_role = check_member_role(request.user, community)
    if community.is_approved == False:
        return redirect('restricted')    
    else:
        form = CreateProjectNoteForm(request.POST or None)

        if request.method == "POST":
            if form.data['note']:
                if form.is_valid():
                    data = form.save(commit=False)
                    data.community = community
                    data.project = project
                    data.sender = request.user
                    data.save()

            # Set private project to contributor view
            if project.project_privacy == 'Private':
                project.project_privacy = 'Contributor'
                project.save()

            add_remove_labels(request, project, community)
            
            if notices:
                if not project.has_labels():
                    for notice in notices:
                        notice.archived = False
                        notice.save()
                else:
                    # add community to project contributors
                    contributors = ProjectContributors.objects.get(project=project)
                    contributors.communities.add(community)
                    contributors.save()

                    # Archive Notices
                    for notice in notices:
                        notice.archived = True
                        notice.save()
                    
                    # If community is added as a contrib but not notified, they can apply labels and this will create a status for them.
                    #reset status
                    if ProjectStatus.objects.filter(project=project, community=community).exists():
                        status = ProjectStatus.objects.get(project=project, community=community)
                        status.seen = True
                        status.status = 'labels_applied'
                        status.save()
            else:
                comm_title = 'Labels have been applied to the project ' + truncated_project_title + ' ...'
                ActionNotification.objects.create(title=comm_title, notification_type='Projects', community=community, reference_id=reference_id)

            # send email to project creator
            send_email_labels_applied(request, project, community)
            messages.add_message(request, messages.SUCCESS, "Labels applied!")

            # Adds activity to Hub Activity
            HubActivity.objects.create(
                action_user_id=request.user.id,
                action_type="Label(s) Applied",
                community_id=community.id,
                action_account_type='community',
                project_id=project.id
            )

            return redirect('apply-labels', community.id, project.unique_id)

    context = {
        'member_role': member_role,
        'community': community,
        'project': project,
        'creator': creator,
        'bclabels': bclabels,
        'tklabels': tklabels,
        'notes': notes,
        'form': form,
    }
    return render(request, 'communities/apply-labels.html', context)

@login_required(login_url='login')
@member_required(roles=['admin', 'editor', 'viewer'])
def connections(request, pk):
    community = get_community(pk)
    member_role = check_member_role(request.user, community)

    communities = Community.objects.none()

    institution_ids = community.contributing_communities.exclude(institutions__id=None).values_list('institutions__id', flat=True)
    researcher_ids = community.contributing_communities.exclude(researchers__id=None).values_list('researchers__id', flat=True)

    institutions = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').filter(id__in=institution_ids)
    researchers = Researcher.objects.select_related('user').filter(id__in=researcher_ids)

    project_ids = community.contributing_communities.values_list('project__unique_id', flat=True)
    contributors = ProjectContributors.objects.filter(project__unique_id__in=project_ids)
    for c in contributors:
        communities = c.communities.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').exclude(id=community.id)

    context = {
        'member_role': member_role,
        'community': community,
        'researchers': researchers,
        'institutions': institutions,
        'communities': communities,
    }
    return render(request, 'communities/connections.html', context)
        
# show community Labels in a PDF
@login_required(login_url='login')
@member_required(roles=['admin', 'editor', 'viewer'])
def labels_pdf(request, pk):
    community = get_community(pk)
    if community.is_approved:
        bclabels = BCLabel.objects.filter(community=community, is_approved=True)
        tklabels = TKLabel.objects.filter(community=community, is_approved=True)

        template_path = 'snippets/pdfs/community-labels.html'
        context = {'community': community, 'bclabels': bclabels, 'tklabels': tklabels,}

        # Create a Django response object, and specify content_type as pdf
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="labels.pdf"'

        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        pisa_status = pisa.CreatePDF(html, dest=response, encoding='UTF-8') # create a pdf
        # if error then show view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('restricted')

@login_required(login_url='login')
@member_required(roles=['admin', 'editor', 'viewer'])
def download_labels(request, pk):
    community = get_community(pk)
    if not community.is_approved or dev_prod_or_local(request.get_host()) == 'DEV':
        return redirect('restricted')
    else:
        return download_labels_zip(community)