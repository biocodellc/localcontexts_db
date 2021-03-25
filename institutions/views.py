from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Institution
from researchers.models import Researcher
from projects.models import Project, ProjectContributors
from bclabels.models import BCNotice
from tklabels.models import TKNotice

from .forms import CreateInstitutionForm, UpdateInstitutionForm
from projects.forms import CreateProjectForm

@login_required(login_url='login')
def connect_institution(request):
    return render(request, 'institutions/connect-institution.html')

@login_required(login_url='login')
def create_institution(request):
    if request.method == 'POST':
        form = CreateInstitutionForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.institution_creator = request.user
            data.save()
            return redirect('dashboard')
    else:
        form = CreateInstitutionForm()
        return render(request, 'institutions/create-institution.html', {'form': form})

@login_required(login_url='login')
def institution_registry(request):
    institutions = Institution.objects.all()
    return render(request, 'institutions/institution-registry.html', {'institutions': institutions})

# Dashboard / Activity
@login_required(login_url='login')
def institution_dashboard(request, pk):
    institution = Institution.objects.get(id=pk)
    return render(request, 'institutions/dashboard.html', {'institution': institution})

# Update institution
@login_required(login_url='login')
def update_institution(request, pk):
    institution = Institution.objects.get(id=pk)
    return render(request, 'institutions/update-institution.html', {'institution': institution})

# Notices
@login_required(login_url='login')
def institution_notices(request, pk):
    institution = Institution.objects.get(id=pk)
    return render(request, 'institutions/notices.html', {'institution': institution})

# Projects
@login_required(login_url='login')
def institution_projects(request, pk):
    institution = Institution.objects.get(id=pk)
    contribs = ProjectContributors.objects.filter(institution=institution)

    context = {
        'institution': institution,
        'contribs': contribs,
    }
    return render(request, 'institutions/projects.html', context)

# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    institution = Institution.objects.get(id=pk)

    if request.method == "POST":
        form = CreateProjectForm(request.POST or None)
        if form.is_valid():
            data = form.save(commit=False)
            data.save()

            notices_selected = request.POST.getlist('checkbox-notice')
            # if tknotice: create notice
            # if bcnotice: create notice
            # if both: create both
            for notice in notices_selected:
                if notice == 'bcnotice':
                    BCNotice.objects.create(placed_by_institution=institution, project=data)
                if notice == 'tknotice':
                    TKNotice.objects.create(placed_by_institution=institution, project=data)

            ProjectContributors.objects.create(project=data, institution=institution)
            return redirect('institution-projects', institution.id)
    else:
        form = CreateProjectForm()

    context = {
        'institution': institution,
        'form': form,
    }
    return render(request, 'institutions/create-project.html', context)

