from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Researcher
from .forms import ConnectResearcherForm, CreateProjectForm

@login_required(login_url='login')
def connect_researcher(request):
    form = ConnectResearcherForm()

    if request.method == "POST":
        form = ConnectResearcherForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('researcher-dashboard')

    return render(request, 'researchers/connect-researcher.html', {'form': form})

@login_required(login_url='login')
def researcher_dashboard(request, pk):
    # is current user a researcher?
    researcher = Researcher.objects.get(id=pk)

    return render(request, 'researchers/dashboard.html', {'researcher': researcher})

@login_required(login_url='login')
def researcher_notices(request, pk):
    researcher = Researcher.objects.get(id=pk)

    projects = researcher.projects.all()
    print(projects)

    return render(request, 'researchers/notices.html', {'researcher': researcher})

@login_required(login_url='login')
def researcher_relationships(request, pk):
    researcher = Researcher.objects.get(id=pk)

    return render(request, 'researchers/relationships.html', {'researcher': researcher})

@login_required(login_url='login')
def add_notice(request, pk):
    researcher = Researcher.objects.get(id=pk)
    form = CreateProjectForm()

    if request.method == 'POST':
        form = CreateProjectForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()

            # Saves project to researcher's list of projects
            researcher = Researcher.objects.get(user=request.user)
            researcher.projects.add(obj)

            projects = researcher.projects.all()
    
    context = {
        'researcher': researcher,
        'form': form,
        'projects': projects,
    }

    return render(request, 'researchers/add-notice.html', context)
