from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.utils import is_user_researcher

from bclabels.models import BCNotice
from notifications.models import CommunityNotification

from .models import Researcher
from .forms import *

@login_required(login_url='login')
def connect_researcher(request):
    researcher = is_user_researcher(request.user)
    
    if researcher == False:
        if request.method == "POST":
            form = ConnectResearcherForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.user = request.user

                if '-' in data.orcid:
                    data.save()
                else:
                    data.orcid = '-'.join([data.orcid[i:i+4] for i in range(0, len(data.orcid), 4)])
                    data.save()

                return redirect('dashboard')
        else:
            form = ConnectResearcherForm()

        return render(request, 'researchers/connect-researcher.html', {'form': form})
    else:
        return redirect('researcher-dashboard', researcher.id)

@login_required(login_url='login')
def researcher_dashboard(request, pk):
    # TODO: is current user a researcher?
    researcher = Researcher.objects.get(id=pk)

    return render(request, 'researchers/dashboard.html', {'researcher': researcher})

@login_required(login_url='login')
def update_researcher(request, pk):
    researcher = Researcher.objects.get(id=pk)

    if request.method == 'POST':
        update_form = UpdateResearcherForm(request.POST, instance=researcher)

        if update_form.is_valid():
            data = update_form.save(commit=False)
            if '-' in data.orcid:
                data.save()
            else: 
                data.orcid = '-'.join([data.orcid[i:i+4] for i in range(0, len(data.orcid), 4)])
                data.save()

            messages.add_message(request, messages.SUCCESS, 'Updated!')
            return redirect('researcher-update', researcher.id)
    else:
        update_form = UpdateResearcherForm(instance=researcher)
    
    context = {
        'update_form': update_form,
        'researcher': researcher,
    }
    return render(request, 'researchers/update-researcher.html', context)

# TODO: display labels only if they have been approved by community
@login_required(login_url='login')
def researcher_notices(request, pk):
    researcher = Researcher.objects.get(id=pk)
    projects = Project.objects.all()

    #TODO: Fix this to display only projects where target researcher is the contributor

    context = {
        'researcher': researcher,
        'projects': projects,
    }

    return render(request, 'researchers/notices.html', context)

#TODO: Fix this view
@login_required(login_url='login')
def add_notice(request, pk):
    researcher = Researcher.objects.get(id=pk)

    if request.method == 'POST':
        proj_form = CreateProjectForm(request.POST)

        if proj_form.is_valid():            
            proj = proj_form.save(commit=False)
            proj.save()

            # Saves project to researcher's list of projects
            researcher = Researcher.objects.get(user=request.user)
            # researcher.projects.add(proj)

            #TODO: If user in a contrib for a project, display projects

            message = request.POST.get('contrib-message') # Get value of message
            
            created_notice = BCNotice.objects.create(project=proj, placed_by_researcher=researcher, message=message)

            # Send community notification
            title = "A BC notice has been placed by " + str(researcher)
            #TODO: Create a community notification based on project contrib
            # CommunityNotification.objects.create(community=contrib.community, notification_type='Requests', title=title)

            return redirect('researcher-notices', researcher.id)
    else:
        proj_form = CreateProjectForm()
        
    context = {
        'researcher': researcher,
        'proj_form': proj_form,
    }

    return render(request, 'researchers/add-notice.html', context)

@login_required(login_url='login')
def researcher_relationships(request, pk):
    researcher = Researcher.objects.get(id=pk)

    return render(request, 'researchers/relationships.html', {'researcher': researcher})
