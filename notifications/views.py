from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from communities.models import *
from accounts.models import UserAffiliation
from helpers.emails import send_membership_email
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

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