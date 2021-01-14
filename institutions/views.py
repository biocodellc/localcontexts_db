from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from institutions.models import Institution

@login_required(login_url='login')
def connect_institution(request):
    return render(request, 'institutions/connect-institution.html')

@login_required(login_url='login')
def create_institution(request):
    return render(request, 'institutions/create-institution.html')

@login_required(login_url='login')
def institution_registry(request):
    institutions = Institution.objects.all()
    return render(request, 'institutions/institution-registry.html', {'institutions': institutions})

