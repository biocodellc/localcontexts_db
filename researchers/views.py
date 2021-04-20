from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.utils import is_user_researcher

from bclabels.models import BCNotice
from tklabels.models import TKNotice
from notifications.models import CommunityNotification
from projects.models import ProjectContributors
from projects.forms import CreateProjectForm, ProjectContributorsForm

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

@login_required(login_url='login')
def researcher_notices(request, pk):
    researcher = Researcher.objects.get(id=pk)
    context = {'researcher': researcher,}
    return render(request, 'researchers/notices.html', context)

@login_required(login_url='login')
def researcher_activity(request, pk):
    researcher = Researcher.objects.get(id=pk)
    bcnotices = BCNotice.objects.filter(placed_by_researcher=researcher)
    tknotices = TKNotice.objects.filter(placed_by_researcher=researcher)

    context = {
        'researcher': researcher,
        'bcnotices': bcnotices,
        'tknotices': tknotices,
    }
    return render(request, 'researchers/activity.html', context)


# TODO: display labels only if they have been approved by community
@login_required(login_url='login')
def researcher_projects(request, pk):
    researcher = Researcher.objects.get(id=pk)
    contribs = ProjectContributors.objects.filter(researcher=researcher)
    bcnotices = BCNotice.objects.filter(placed_by_researcher=researcher)

    context = {
        'researcher': researcher,
        'contribs': contribs,
        'bcnotices': bcnotices,
    }

    return render(request, 'researchers/projects.html', context)

@login_required(login_url='login')
def create_project(request, pk):
    researcher = Researcher.objects.get(id=pk)

    if request.method == 'POST':
        proj_form = CreateProjectForm(request.POST)
        contrib_form = ProjectContributorsForm(request.POST)

        if proj_form.is_valid() and contrib_form.is_valid():            
            proj = proj_form.save(commit=False)
            proj.project_creator = request.user
            contrib_data = contrib_form.save(commit=False)
            proj.save()
            contrib_data.save()

            contrib = ProjectContributors.objects.create(project=proj, researcher=researcher, community=contrib_data.community)            
            message = request.POST.get('contrib-message') # Get value of message

            notices_selected = request.POST.getlist('checkbox-notice')

            for notice in notices_selected:
                if notice == 'bcnotice':
                    bc_notice = BCNotice.objects.create(placed_by_researcher=researcher, project=proj)
                    bc_notice.communities.add(contrib_data.community)

                    # Send community notification
                    title = "A BC notice has been placed by " + str(researcher.user.get_full_name())
                    CommunityNotification.objects.create(community=contrib_data.community, sender=request.user, notification_type='Requests', title=title)

                if notice == 'tknotice':
                    tk_notice = TKNotice.objects.create(placed_by_researcher=researcher, project=proj)
                    tk_notice.communities.add(contrib_data.community)

                    title = "A TK notice has been placed by " + str(researcher.user.get_full_name())
                    CommunityNotification.objects.create(community=contrib_data.community, sender=request.user, notification_type='Requests', title=title)

            return redirect('researcher-notices', researcher.id)
    else:
        proj_form = CreateProjectForm()
        contrib_form = ProjectContributorsForm()
        
    context = {
        'researcher': researcher,
        'proj_form': proj_form,
        'contrib_form':contrib_form,
    }

    return render(request, 'researchers/add-notice.html', context)

@login_required(login_url='login')
def researcher_relationships(request, pk):
    researcher = Researcher.objects.get(id=pk)

    return render(request, 'researchers/relationships.html', {'researcher': researcher})
