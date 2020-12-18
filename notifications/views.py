from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from communities.models import UserCommunity, Community

@login_required(login_url='login')
def show_notification(request, pk):
    n = UserNotification.objects.get(id=pk)

    if request.method == 'POST':
        comm = n.community.id
        
        if n.notification_type == 'invitation':
            # Add community to UserCommunity
            u = UserCommunity.objects.get(user=n.to_user)
            u.communities.add(comm)
            u.save()

            # TODO: Accommodate other roles,
            # Mark member invitation or member request as accepted,
            # Notify other user that an invitation has been accepted

            # Add member as viewer to community
            c = Community.objects.get(id=comm)
            c.viewers.add(n.to_user)
            u.save()

            return render(request, 'notifications/notification.html', {'notification': n})
        
        elif n.notification_type == 'request':
            # Add community to UserCommunity
            u = UserCommunity.objects.get(user=n.from_user)
            u.communities.add(comm)
            u.save()

            # Add member as viewer to community
            c = Community.objects.get(id=comm)
            c.viewers.add(n.from_user)
            u.save()

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
