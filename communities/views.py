from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# from .forms import CreateCommunityForm
from .models import Community

@login_required
def connect_community(request):
    return render(request, 'communities/connect-community.html')

@login_required
def create_community(request):
    return render(request, 'communities/create-community.html')


@login_required
def community_registry(request):
    communities = Community.objects.all()

    context = {
        'communities': communities
    }
    return render(request, 'communities/community-registry.html', context)

