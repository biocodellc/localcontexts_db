from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def connect_institution(request):
    return render(request, 'institutions/connect-institution.html')
