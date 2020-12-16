from django.shortcuts import render, redirect
from .models import *

def show_notification(request, pk):
    n = UserNotification.objects.get(id=pk)
    return render(request, 'notifications/notification.html', {'notification': n})

def delete_notification(request, pk):
    n = UserNotification.objects.get(id=pk)
    n.viewed = True
    n.save()
    return redirect('dashboard')
