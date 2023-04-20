from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from communities.models import InviteMember
from notifications.models import UserNotification
from localcontexts.utils import dev_prod_or_local
from .downloads import download_otc_notice

def restricted_view(request, exception=None):
    return render(request, '403.html', status=403)

@login_required(login_url='login')
def delete_member_invite(request, pk):
    invite = InviteMember.objects.get(id=pk)
    
    # Delete relevant UserNotification
    if UserNotification.objects.filter(to_user=invite.receiver, from_user=invite.sender, notification_type='invitation', reference_id=pk).exists():
        notification = UserNotification.objects.get(to_user=invite.receiver, notification_type='invitation', reference_id=pk)
        notification.delete()

    invite.delete()

    if '/communities/' in request.META.get('HTTP_REFERER'):
        return redirect('member-requests', invite.community.id)
    else:
        return redirect('institution-member-requests', invite.institution.id)
    

@login_required(login_url='login')
def download_open_collaborate_notice(request, perm):
    # perm will be a 1 or 0
    has_permission = bool(perm)
    if dev_prod_or_local(request.get_host()) == 'DEV' or not has_permission:
        return redirect('restricted')
    else:
        return download_otc_notice(request)