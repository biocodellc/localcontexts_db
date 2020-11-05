from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def connect_community(request):
    return render(request, 'communities/connect-community.html')
