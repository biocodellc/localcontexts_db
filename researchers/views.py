from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def connect_researcher(request):
    return render(request, 'researchers/connect-researcher.html')
