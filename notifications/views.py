from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from communities.models import *

@login_required(login_url='login')
def show_notification(request, pk):
    n = UserNotification.objects.get(id=pk)

    if request.method == 'POST':
        comm = n.community.id

        # TODO: Accommodate other roles besides just viewer
        
        if n.notification_type == 'invitation':
            i = InviteMember.objects.get(id=n.reference_id)
            i.status = 'accepted'
            i.save()

            # Add community to UserCommunity
            u = UserCommunity.objects.get(user=n.to_user)
            u.communities.add(comm)
            u.save()

            # Add member as viewer to community
            c = Community.objects.get(id=comm)
            c.viewers.add(n.to_user)
            u.save()

            return render(request, 'notifications/notification.html', {'notification': n})
        
        elif n.notification_type == 'request':
            j = CommunityJoinRequest.objects.get(id=n.reference_id)
            j.status = 'accepted'
            j.save()

            # Add community to UserCommunity
            u = UserCommunity.objects.get(user=n.from_user)
            u.communities.add(comm)
            u.save()

            # Add member as viewer to community
            c = Community.objects.get(id=comm)
            c.viewers.add(n.from_user)
            u.save()

            return render(request, 'notifications/notification.html', {'notification': n})
        
        elif n.notification_type == 'create':
            new_community = Community.objects.get(id=comm)
            new_community.is_approved = True
            new_community.save()

            return render(request, 'notifications/notification.html', {'notification': n})


    context = {
        'notification': n,
    }

    return render(request, 'notifications/notification.html', context)

@login_required(login_url='login')
def delete_notification(request, pk):
    n = UserNotification.objects.get(id=pk)
    n.viewed = True
    n.save()
    return redirect('dashboard')
