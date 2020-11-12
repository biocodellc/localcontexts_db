from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def connect_community(request):
    return render(request, 'communities/connect-community.html')

@login_required
def create_community(request):
    return render(request, 'communities/create-community.html')

@login_required
def community_registry(request):
    return render(request, 'communities/community-registry.html')

