from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *

@login_required(login_url='login')
def show_notification(request, pk):
    n = UserNotification.objects.get(id=pk)
    return render(request, 'notifications/notification.html', {'notification': n})

@login_required(login_url='login')
def delete_notification(request, pk):
    n = UserNotification.objects.get(id=pk)
    n.viewed = True
    n.save()
    return redirect('dashboard')
