from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from communities.models import *
from accounts.models import UserAffiliation
from helpers.emails import send_membership_email
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

@login_required(login_url='login')
def show_notification(request, pk):
    n = UserNotification.objects.get(id=pk)
    sent_to = n.to_user
    # sent_from = n.from_user
    sent_to_affiliation = UserAffiliation.objects.get(user=sent_to)
    # sent_from_affiliation = UserAffiliation.objects.get(user=sent_from)

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
@csrf_exempt
def read_org_notification(request, pk):
    n = ActionNotification.objects.get(id=pk)
    n.viewed = True
    n.save()
    return render(request, 'notifications/action-read.html')