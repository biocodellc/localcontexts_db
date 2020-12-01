from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .forms import CreateCommunityForm
from .models import Community

@login_required
def connect_community(request):
    return render(request, 'communities/connect-community.html')

@login_required
def create_community(request):

    form = CreateCommunityForm()

    if request.method == "POST":
        form = CreateCommunityForm(request.POST)
        if form.is_valid():
            form.save()

    context = {'form': form}
    return render(request, 'communities/create-community.html', context)


@login_required
def community_registry(request):
    communities = Community.objects.all()

    context = {'communities': communities}
    return render(request, 'communities/community-registry.html', context)

@login_required
def community_dashboard(request, pk):
    community = Community.objects.get(id=pk)
    members = community.members.count()

    context = {
        'community': community,
        'members': members,
    }
    return render(request, 'communities/community.html', context)

