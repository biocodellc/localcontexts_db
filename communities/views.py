from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *

@login_required(login_url='login')
def connect_community(request):
    return render(request, 'communities/connect-community.html')

@login_required(login_url='login')
def create_community(request):

    form = CreateCommunityForm()

    if request.method == "POST":
        form = CreateCommunityForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.community_creator = request.user
            obj.save()
            return redirect('community-registry')

    context = {'form': form}
    return render(request, 'communities/create-community.html', context)


@login_required(login_url='login')
def community_registry(request):
    communities = Community.objects.all()
    context = {'communities': communities}
    return render(request, 'communities/community-registry.html', context)

@login_required(login_url='login')
def community_dashboard(request, pk):
    community = Community.objects.get(id=pk)

    context = {
        'community': community,
    }
    return render(request, 'communities/community.html', context)

@login_required(login_url='login')
def community_members(request, pk):
    community = Community.objects.get(id=pk)

    context = {
        'community': community,
    }

    return render(request, 'communities/members.html', context)

@login_required(login_url='login')
def add_members(request, pk):
    community = Community.objects.get(id=pk)
    form = InviteMemberForm()

    if request.method == "POST":
        form = InviteMemberForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.sender = request.user
            obj.status = 'sent'
            obj.community = community
            obj.save()
            return redirect('dashboard')

    context = {
        'form': form,
        'community': community,
    }
    return render(request, 'communities/add-member.html', context)

# @login_required(login_url='login')
# def accept_invitation(request, pk):
#     invite = InviteMember.objects.filter(id=pk)
#     invite.status = 'accepted'
#     invite.save()

#     return render(request, 'partials/accept-invite.html')
