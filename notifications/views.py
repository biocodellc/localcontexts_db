from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from communities.models import *
from accounts.models import UserAffiliation
from helpers.emails import send_membership_email
from .utils import send_community_approval_notification
from django.views.decorators.csrf import csrf_exempt

@login_required(login_url='login')
def show_notification(request, pk):
    n = UserNotification.objects.get(id=pk)
    sent_to = n.to_user
    sent_from = n.from_user
    sent_to_affiliation = UserAffiliation.objects.get(user=sent_to)
    sent_from_affiliation = UserAffiliation.objects.get(user=sent_from)

    if request.method == 'POST':
        if n.community:
            community_id = n.community.id
            community = Community.objects.get(id=community_id)

            if n.notification_type == 'Invitation':
                invite = InviteMember.objects.get(id=n.reference_id) #Use reference id to find id of Invite Member instance
                invite.status = 'accepted'
                invite.save()

                # Add community to UserAffiliation
                sent_to_affiliation.communities.add(community)
                sent_to_affiliation.save()

                # Add user as target role to community.
                if n.role == 'viewer':
                    community.viewers.add(sent_to)
                elif n.role == 'admin':
                    community.admins.add(sent_to)
                elif n.role == 'editor':
                    community.editors.add(sent_to)
                community.save()

                # Send email letting user know they are a member
                send_membership_email(request, community, sent_to, n.role)

                return render(request, 'notifications/read.html', {'notification': n})

            elif n.notification_type == 'Request':
                join_request = JoinRequest.objects.get(id=n.reference_id)
                join_request.status = 'accepted'
                join_request.save()

                # Add community to UserAffiliation
                sent_from_affiliation.communities.add(community)
                sent_from_affiliation.save()

                radio_value = request.POST.get('role')

                if radio_value == 'admin':
                    community.admins.add(sent_from)
                elif radio_value == 'editor':
                    community.editors.add(sent_from)
                elif radio_value == 'viewer':
                    community.viewers.add(sent_from)
                community.save()

                # Send email letting user know they are a member
                send_membership_email(request, community, sent_from, n.role)

                return render(request, 'notifications/read.html', {'notification': n})

            elif n.notification_type == 'Create':
                new_community = Community.objects.get(id=community_id)
                new_community.is_approved = True
                new_community.save()
                # Sends email
                send_community_approval_notification(new_community.community_creator, new_community)
                return render(request, 'notifications/read.html', {'notification': n})

        if n.institution:
            institution_id = n.institution.id
            institution = Institution.objects.get(id=institution_id)

            if n.notification_type == 'Invitation':
                invite = InviteMember.objects.get(id=n.reference_id) #Use reference id to find id of Invite Member instance
                invite.status = 'accepted'
                invite.save()

                # Add institution to UserAffiliation
                sent_to_affiliation.institutions.add(institution)
                sent_to_affiliation.save()

                # Add user as target role to institution.
                if n.role == 'viewer':
                    institution.viewers.add(sent_to)
                elif n.role == 'admin':
                    institution.admins.add(sent_to)
                elif n.role == 'editor':
                    institution.editors.add(sent_to)
                institution.save()

                # Send email letting user know they are a member
                send_membership_email(request, institution, sent_to, n.role)

                return render(request, 'notifications/read.html', {'notification': n})

            elif n.notification_type == 'Request':
                join_request = JoinRequest.objects.get(id=n.reference_id)
                join_request.status = 'accepted'
                join_request.save()

                # Add institution to UserAffiliation
                sent_from_affiliation.institutions.add(institution)
                sent_from_affiliation.save()

                # get radio btn value from template
                radio_value = request.POST.get('role')
                if radio_value == 'admin':
                    institution.admins.add(sent_from)
                elif radio_value == 'editor':
                    institution.editors.add(sent_from)
                elif radio_value == 'viewer':
                    institution.viewers.add(sent_from)
                institution.save()

                # Send email letting user know they are a member
                send_membership_email(request, institution, sent_from, n.role)

                return render(request, 'notifications/read.html', {'notification': n})
                
    return render(request, 'notifications/notification.html', { 'notification': n })

@login_required(login_url='login')
def read_notification(request, pk):
    n = UserNotification.objects.get(id=pk)
    n.viewed = True
    n.save()
    return render(request, 'notifications/read.html', {'notification': n})


@login_required(login_url='login')
def delete_notification(request, pk):
    n = UserNotification.objects.get(id=pk)
    n.delete()
    return redirect('dashboard')

@login_required(login_url='login')
def show_notification_community(request, cid, pk):
    n = ActionNotification.objects.get(id=pk)
    community = Community.objects.get(id=cid)
    context = {
        'n': n,
        'community':community,
    }
    return render(request, 'notifications/community-notification.html', context)

@login_required(login_url='login')
@csrf_exempt
def read_notification_community(request, cid, pk):
    n = ActionNotification.objects.get(id=pk)
    community = Community.objects.get(id=cid)
    n.viewed = True
    n.save()
    
    context = {
        'n': n,
        'community':community,
    }
    return render(request, 'notifications/comm-read.html', context)

@login_required(login_url='login')
@csrf_exempt
def read_institution_notification(request, iid, pk):
    n = ActionNotification.objects.get(id=pk)
    institution = Institution.objects.get(id=iid)
    n.viewed = True
    n.save()
    
    context = {
        'n': n,
        'institution':institution,
    }
    return render(request, 'notifications/inst-read.html', context)

@login_required(login_url='login')
@csrf_exempt
def read_researcher_notification(request, rid, pk):
    n = ActionNotification.objects.get(id=pk)
    researcher = Researcher.objects.get(id=rid)
    n.viewed = True
    n.save()
    
    context = {
        'n': n,
        'researcher':researcher,
    }
    return render(request, 'notifications/researcher-read.html', context)
