from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.contrib import messages
from .forms import *
from .models import *
from .utils import get_site_admin_email, checkif_community_in_user_community, checkif_invite_exists


@login_required(login_url='login')
def connect_community(request):
    return render(request, 'communities/connect-community.html')

@login_required(login_url='login')
def create_community(request):
    form = CreateCommunityForm()

    if request.method == "POST":
        form = CreateCommunityForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.community_creator = request.user
            obj.save()

            site_admin_email = get_site_admin_email()

            # Send email to site admin
            template = render_to_string('snippets/community-application.html', { 'obj' : obj })
            send_mail(
                'New Community Application', 
                template, 
                settings.EMAIL_HOST_USER, 
                site_admin_email, 
                fail_silently=False)

            return redirect('community-registry')

    context = {'form': form}
    return render(request, 'communities/create-community.html', context)


def community_registry(request):
    communities = Community.objects.filter(is_approved=True, is_publicly_listed=True)

    if request.method == 'POST':
        # TODO: Change the button so the user can only submit a request once.
        buttonid = request.POST.get('commid')
        target_community = Community.objects.get(id=buttonid)
        main_admin = target_community.community_creator

        current_user = UserCommunity.objects.get(user=request.user)
        user_communities = current_user.communities.all()

        if target_community in user_communities:
            print('#########  YOU ARE ALREADY A MEMBER OF THIS COMMUNITY ###########')
        else:
            req = CommunityJoinRequest.objects.create(user_from=request.user, target_community=target_community, user_to=main_admin)
            req.save()

        return redirect('community-registry')

    context = {'communities': communities}
    return render(request, 'communities/community-registry.html', context)

@login_required(login_url='login')
def community_dashboard(request, pk):
    community = Community.objects.get(id=pk)

    context = {
        'community': community,
    }
    return render(request, 'communities/community.html', context)

@login_required(login_url='login')
def update_community(request, pk):
    community = Community.objects.get(id=pk)

    context = {
        'community': community,
    }
    return render(request, 'communities/update-community.html', context)


@login_required(login_url='login')
def community_members(request, pk):
    community = Community.objects.get(id=pk)
    form = InviteMemberForm()

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
            else: 
                messages.add_message(request, messages.INFO, 'This user has already been invited to this community!')
        else:
            messages.add_message(request, messages.ERROR, 'User Already A Member')


    context = {
        'community': community,
        'form': form,
    }

    return render(request, 'communities/members.html', context)

@login_required(login_url='login')
def community_requests(request, pk):
    community = Community.objects.get(id=pk)
    context = {
        'community': community,
    }
    return render(request, 'communities/requests.html', context)

@login_required(login_url='login')
def community_labels(request, pk):
    community = Community.objects.get(id=pk)
    context = {
        'community': community,
    }
    return render(request, 'communities/labels.html', context)

def community_relationships(request, pk):
    community = Community.objects.get(id=pk)
    context = {
        'community': community,
    }
    return render(request, 'communities/relationships.html', context)
