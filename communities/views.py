from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.contrib import messages

from accounts.models import UserAffiliation
from notifications.models import CommunityNotification
from bclabels.models import BCNotice, BCLabel
from bclabels.forms import CustomiseLabelForm, ApproveAndEditLabelForm
from bclabels.utils import check_bclabel_type
# from researchers.models import ProjectContributors

from .forms import *
from .models import *
from .utils import *


@login_required(login_url='login')
def connect_community(request):
    return render(request, 'communities/connect-community.html')

@login_required(login_url='login')
def create_community(request):
    if request.method == "POST":
        form = CreateCommunityForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.community_creator = request.user
            obj.save()

            template = render_to_string('snippets/community-application.html', { 'obj' : obj })
            send_mail(
                'New Community Application', 
                template, 
                settings.EMAIL_HOST_USER, 
                [settings.SITE_ADMIN_EMAIL], 
                fail_silently=False)

            return redirect('dashboard')
    else:
        form = CreateCommunityForm()

    context = {'form': form}
    return render(request, 'communities/create-community.html', context)


def community_registry(request):
    communities = Community.objects.filter(is_approved=True, is_publicly_listed=True)

    if request.user.is_authenticated:
        current_user = UserAffiliation.objects.get(user=request.user)
        user_communities = current_user.communities.all()
        # all_requests = CommunityJoinRequest.objects.all()

        if request.method == 'POST':
            # TODO: Change the button so the user can only submit a request once.
            # Check if CommunityJoinRequest exists
            # If it exists, show different button
            buttonid = request.POST.get('commid')
            target_community = Community.objects.get(id=buttonid)
            main_admin = target_community.community_creator

            req = CommunityJoinRequest.objects.create(user_from=request.user, target_community=target_community, user_to=main_admin)
            req.save()

            return redirect('community-registry')
    else:
        return render(request, 'communities/community-registry.html', {'communities': communities})

    context = {
        'communities': communities,
        'user_communities': user_communities,
        # 'all_requests': all_requests,
    }
    return render(request, 'communities/community-registry.html', context)

@login_required(login_url='login')
def community_dashboard(request, pk):
    community = Community.objects.get(id=pk)
    n = CommunityNotification.objects.filter(community=community)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        context = {
            'community': community,
            'notifications': n,
            'member_role': member_role,
        }
        return render(request, 'communities/community.html', context)

@login_required(login_url='login')
def update_community(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'editor' or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    
    else:
        update_form = UpdateCommunityForm(instance=community)
        if member_role == 'admin': # Only admins can change the form 
            if request.method == "POST":
                update_form = UpdateCommunityForm(request.POST, instance=community)
                if update_form.is_valid():
                    update_form.save()
                    messages.add_message(request, messages.SUCCESS, 'Updated!')
                else:
                    update_form = UpdateCommunityForm(instance=community)

        context = {
            'community': community,
            'update_form': update_form,
            'member_role': member_role,
        }
        return render(request, 'communities/update-community.html', context)


@login_required(login_url='login')
def community_members(request, pk):
    community = Community.objects.get(id=pk)
    member_role = check_member_role(request.user, community)
    return render(request, 'communities/members.html', {'community': community, 'member_role': member_role,})

@login_required(login_url='login')
def add_member(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})

    else:
        if request.method == "POST":
            form = InviteMemberForm(request.POST or None)
            receiver = request.POST.get('receiver')
            user_check = checkif_community_in_user_community(receiver, community)
            
            if user_check == False: # If user is not community member
                check_invitation = checkif_invite_exists(receiver, community) # Check to see if invitation already exists

                if check_invitation == False: # If invitation does not exist, save form.
                    if form.is_valid():
                        obj = form.save(commit=False)
                        obj.sender = request.user
                        obj.status = 'sent'
                        obj.community = community
                        obj.save()

                        messages.add_message(request, messages.INFO, 'Invitation Sent!')
                        return render(request, 'communities/add-member.html', {'community': community, 'form': form,})

                else: 
                    messages.add_message(request, messages.INFO, 'This user has already been invited to this community!')
                    return render(request, 'communities/add-member.html', {'community': community, 'form': form,})
            else:
                messages.add_message(request, messages.ERROR, 'This user is already a member.')
                return render(request, 'communities/add-member.html', {'community': community, 'form': form,})
        else:
            form = InviteMemberForm()

    context = {
        'community': community,
        'form': form,
        'member_role': member_role,
    }
    return render(request, 'communities/add-member.html', context)

@login_required(login_url='login')
def community_requests(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        notices = BCNotice.objects.filter(communities=community)
        context = {
            'notices': notices,
            'community': community,
            'member_role': member_role,
        }
        return render(request, 'communities/requests.html', context)
        
#TODO: figure out how to display projects that labels have been applied to / approved
@login_required(login_url='login')
def community_labels(request, pk):
    community = Community.objects.get(id=pk)
    bclabels = BCLabel.objects.filter(community=community)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        if request.method == "POST":
            label_type = request.POST.get('testing-variable')
            return redirect('customise-label', community.id, label_type)

        context = {
            'community': community,
            'member_role': member_role,
            'bclabels': bclabels,
        }
        return render(request, 'communities/labels.html', context)

@login_required(login_url='login')
def customise_label(request, pk, label_type):
    community = Community.objects.get(id=pk)
    bc_type = check_bclabel_type(label_type)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        if request.method == "POST":
            form = CustomiseLabelForm(request.POST)
            if form.is_valid():
                label_form = form.save(commit=False)
                label_form.label_type = bc_type
                label_form.community = community
                label_form.created_by = request.user
                label_form.is_approved = False
                label_form.save()
                return redirect('community-labels', community.id)
        else:
            form = CustomiseLabelForm()

        context = {
            'community': community,
            'label_type': label_type,
            'form': form,
            'member_role': member_role,
        }
        return render(request, 'communities/customise-label.html', context)

@login_required(login_url='login')
def approve_label(request, pk, label_id):
    community = Community.objects.get(id=pk)
    bclabel = BCLabel.objects.get(id=label_id)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        form = ApproveAndEditLabelForm(instance=bclabel)
        if request.method == "POST":
            form = ApproveAndEditLabelForm(request.POST, instance=bclabel)
            if form.is_valid():
                label_form = form.save(commit=False)
                label_form.is_approved = True
                label_form.save()
                return redirect('community-labels', community.id)
        else:
            form = ApproveAndEditLabelForm(instance=bclabel)

        context = {
            'community': community,
            'bclabel': bclabel,
            'member_role': member_role,
            'form': form,
        }
        return render(request, 'communities/approve-label.html', context)

@login_required(login_url='login')
def projects(request, pk):
    community = Community.objects.get(id=pk)
    
    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        notices = community.bcnotice_communities.all()

        context = {
            'community': community, 
            'member_role': member_role,
            'notices': notices,
        }
        return render(request, 'communities/projects.html', context)

@login_required(login_url='login')
def create_project(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        return render(request, 'communities/create-project.html', {'community': community, 'member_role': member_role,})

#TODO: add roles that have access to this page
@login_required(login_url='login')
def community_add_labels(request, pk, notice_id):
    community = Community.objects.get(id=pk)
    notice = BCNotice.objects.get(id=notice_id)
    bclabels = BCLabel.objects.filter(community=community)

    if request.method == "POST":
        label_selected = request.POST.getlist('checkbox-label')
        print(label_selected)
        for choice in label_selected:
            print(choice)
            label = BCLabel.objects.get(id=choice)
            notice.project.bclabels.add(label)
        return redirect('community-projects', community.id)
    
    context = {
        'community': community,
        'notice': notice,
        'bclabels': bclabels,
    }
    return render(request, 'communities/attach-labels.html', context)


@login_required(login_url='login')
def community_relationships(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        context = {
            'community': community,
            'member_role': member_role,
        }
        return render(request, 'communities/relationships.html', context)

def restricted_view(request, pk):
    community = Community.objects.get(id=pk)
    return render(request, 'communities/restricted.html', {'community': community})
