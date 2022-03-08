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

    if request.method == 'POST':
        if n.community:
            comm = n.community.id

            if n.notification_type == 'Invitation':
                i = InviteMember.objects.get(id=n.reference_id) #Use reference id to find id of Invite Member instance
                i.status = 'accepted'
                i.save()

                # Add community to UserAffiliation
                u = UserAffiliation.objects.get(user=n.to_user)
                u.communities.add(comm)
                u.save()

                # Add user as target role to community.
                c = Community.objects.get(id=comm)
                if n.role == 'viewer':
                    c.viewers.add(n.to_user)
                elif n.role == 'admin':
                    c.admins.add(n.to_user)
                elif n.role == 'editor':
                    c.editors.add(n.to_user)
                c.save()

                return render(request, 'notifications/read.html', {'notification': n})

            elif n.notification_type == 'Request':
                j = JoinRequest.objects.get(id=n.reference_id)
                j.status = 'accepted'
                j.save()

                # Add community to UserAffiliation
                u = UserAffiliation.objects.get(user=n.from_user)
                u.communities.add(comm)
                u.save()

                c = Community.objects.get(id=comm)
                radio_value = request.POST.get('role')

                if radio_value == 'admin':
                    c.admins.add(n.from_user)
                elif radio_value == 'editor':
                    c.editors.add(n.from_user)
                elif radio_value == 'viewer':
                    c.viewers.add(n.from_user)
                c.save()

                # Send email letting user know they are a member
                send_membership_email(request, c, n.user_from, n.role)

                return render(request, 'notifications/read.html', {'notification': n})

            elif n.notification_type == 'Create':
                new_community = Community.objects.get(id=comm)
                new_community.is_approved = True
                new_community.save()

                send_community_approval_notification(new_community.community_creator, new_community)

                return render(request, 'notifications/read.html', {'notification': n})

        if n.institution:
            inst = n.institution.id

            if n.notification_type == 'Invitation':
                i = InviteMember.objects.get(id=n.reference_id) #Use reference id to find id of Invite Member instance
                i.status = 'accepted'
                i.save()

                # Add institution to UserAffiliation
                u = UserAffiliation.objects.get(user=n.to_user)
                u.institutions.add(inst)
                u.save()

                # Add user as target role to institution.
                c = Institution.objects.get(id=inst)
                if n.role == 'viewer':
                    c.viewers.add(n.to_user)
                elif n.role == 'admin':
                    c.admins.add(n.to_user)
                elif n.role == 'editor':
                    c.editors.add(n.to_user)
                c.save()

                # Send email letting user know they are a member
                send_membership_email(request, c, n.user_from, n.role)

                return render(request, 'notifications/read.html', {'notification': n})

            elif n.notification_type == 'Request':
                j = JoinRequest.objects.get(id=n.reference_id)
                j.status = 'accepted'
                j.save()

                # Add institution to UserAffiliation
                u = UserAffiliation.objects.get(user=n.from_user)
                u.institutions.add(inst)
                u.save()

                c = Institution.objects.get(id=inst)
                radio_value = request.POST.get('role')

                if radio_value == 'admin':
                    c.admins.add(n.from_user)
                elif radio_value == 'editor':
                    c.editors.add(n.from_user)
                elif radio_value == 'viewer':
                    c.viewers.add(n.from_user)
                c.save()

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
