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

    administrator = community.community_creator
    editors = community.editors.count()
    viewers = community.viewers.count()
    total_members = editors + viewers + 1

    context = {
        'community': community,
        'total_members': total_members,
        'administrator': administrator,
    }
    return render(request, 'communities/community.html', context)

@login_required(login_url='login')
def community_members(request, pk):
    community = Community.objects.get(id=pk)

    administrator = community.community_creator
    all_editors = community.editors.all()
    all_viewers = community.viewers.all()

    editors = community.editors.count()
    viewers = community.viewers.count()
    total_members = editors + viewers + 1

    form = AddCommunityMember()

    context = {
        'community': community,
        'total_members': total_members,
        'administrator': administrator,
        'all_viewers': all_viewers,
        'all_editors': all_editors,
        'form': form,
    }

    return render(request, 'communities/members.html', context)