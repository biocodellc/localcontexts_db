from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from communities.models import *
from accounts.models import UserAffiliation
from .utils import send_community_approval_notification

@login_required(login_url='login')
def show_notification(request, pk):
    n = UserNotification.objects.get(id=pk)

    if request.method == 'POST':
        comm = n.community.id
        
        if n.notification_type == 'invitation':
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

        
        elif n.notification_type == 'request':
            j = CommunityJoinRequest.objects.get(id=n.reference_id)
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

            return render(request, 'notifications/read.html', {'notification': n})

        elif n.notification_type == 'create':
            new_community = Community.objects.get(id=comm)
            new_community.is_approved = True
            new_community.save()

            send_community_approval_notification(new_community.community_creator, new_community)

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
    n = CommunityNotification.objects.get(id=pk)
    community = Community.objects.get(id=cid)
    context = {
        'n': n,
        'community':community,
    }
    return render(request, 'notifications/community-notification.html', context)

@login_required(login_url='login')
def read_notification_community(request, cid, pk):
    n = CommunityNotification.objects.get(id=pk)
    community = Community.objects.get(id=cid)
    n.viewed = True
    n.save()
    
    context = {
        'n': n,
        'community':community,
    }
    return render(request, 'notifications/comm-read.html', context)


# TODO: Do we need to be able to delete requests/ community notifications?
# @login_required(login_url='login')
# def delete_notification_community(request, pk):
#     n = CommunityNotification.objects.get(id=pk)
#     return render(request, 'notifications/community-notification.html', { 'n': n })
