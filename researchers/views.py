from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from bclabels.models import BCNotice

from .models import Researcher
from .forms import *

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

    context = {
        'researcher': researcher,
        'projects': projects,
    }

    return render(request, 'researchers/notices.html', context)

@login_required(login_url='login')
def add_notice(request, pk):
    researcher = Researcher.objects.get(id=pk)

    if request.method == 'POST':
        proj_form = CreateProjectForm(request.POST)
        contrib_form = ProjectContributorsForm(request.POST)

        if proj_form.is_valid() and contrib_form.is_valid():            
            proj = proj_form.save(commit=False)
            contrib = contrib_form.save(commit=False)
            contrib.project = proj

            proj.save()
            contrib.save()

            # Saves project to researcher's list of projects
            researcher = Researcher.objects.get(user=request.user)
            researcher.projects.add(proj)

            message = request.POST.get('contrib-message') # Get value of message
            
            created_notice = BCNotice.objects.create(project=proj, placed_by_researcher=researcher, message=message)

            if contrib.community:
                created_notice.communities.add(contrib.community)
                
            context = {
                'researcher': researcher,
                'proj_form': proj_form,
                'contrib_form': contrib_form,
            }

            return render(request, 'researchers/add-notice.html', context)
    else:
        proj_form = CreateProjectForm()
        contrib_form = ProjectContributorsForm()
        
        context = {
            'researcher': researcher,
            'proj_form': proj_form,
            'contrib_form': contrib_form,
        }

        return render(request, 'researchers/add-notice.html', context)

@login_required(login_url='login')
def researcher_relationships(request, pk):
    researcher = Researcher.objects.get(id=pk)

    return render(request, 'researchers/relationships.html', {'researcher': researcher})
