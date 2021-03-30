from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Institution
from researchers.models import Researcher
from projects.models import Project, ProjectContributors
from bclabels.models import BCNotice
from tklabels.models import TKNotice
from communities.models import Community
from notifications.models import CommunityNotification

from .forms import CreateInstitutionForm, UpdateInstitutionForm
from projects.forms import CreateProjectForm
# from bclabels.forms import AddBCNoticeMessage
# from tklabels.forms import AddTKNoticeMessage

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
    update_form = UpdateInstitutionForm(instance=institution)
    
    if request.method == "POST":
        update_form = UpdateInstitutionForm(request.POST, instance=institution)
        if update_form.is_valid():
            update_form.save()
            messages.add_message(request, messages.SUCCESS, 'Updated!')
        else:
            update_form = UpdateInstitutionForm(instance=institution)
    context = {
        'institution': institution,
        'update_form': update_form,
    }

    return render(request, 'institutions/update-institution.html', context)

# Notices
@login_required(login_url='login')
def institution_notices(request, pk):
    institution = Institution.objects.get(id=pk)
    return render(request, 'institutions/notices.html', {'institution': institution})

# Requests
@login_required(login_url='login')
def institution_requests(request, pk):
    institution = Institution.objects.get(id=pk)
    bcnotices = BCNotice.objects.filter(placed_by_institution=institution)
    tknotices = TKNotice.objects.filter(placed_by_institution=institution)
    context = {
        'institution': institution,
        'bcnotices': bcnotices,
        'tknotices': tknotices,
    }
    return render(request, 'institutions/requests.html', context)

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

            for notice in notices_selected:
                if notice == 'bcnotice':
                    BCNotice.objects.create(placed_by_institution=institution, project=data)
                if notice == 'tknotice':
                    TKNotice.objects.create(placed_by_institution=institution, project=data)

            ProjectContributors.objects.create(project=data, institution=institution)
            return redirect('institution-requests', institution.id)
    else:
        form = CreateProjectForm()

    context = {
        'institution': institution,
        'form': form,
    }
    return render(request, 'institutions/create-project.html', context)

@login_required(login_url='login')
def notify_communities(request, pk, proj_id):
    institution = Institution.objects.get(id=pk)
    project = Project.objects.get(id=proj_id)
    contribs = ProjectContributors.objects.get(project=project, institution=institution)

    bcnotice_exists = BCNotice.objects.filter(project=project).exists()
    tknotice_exists = TKNotice.objects.filter(project=project).exists()

    communities = Community.objects.all()

    if request.method == "POST":
        communities_selected = request.POST.getlist('selected_communities')
        message = request.POST.get('notice_message')

        for community_id in communities_selected:
            title = str(institution.institution_name) + " has placed a notice"

            community = Community.objects.get(id=community_id)

            # Create notification
            CommunityNotification.objects.create(community=community, notification_type='Requests', title=title)
            
            # add community to bclabel instance
            if bcnotice_exists:
                bcnotices = BCNotice.objects.filter(project=project)
                for bcnotice in bcnotices:
                    bcnotice.communities.add(community)
                    bcnotice.message = message
                    bcnotice.save()
            
            # add community to tklabel instance
            if tknotice_exists:
                tknotices = TKNotice.objects.filter(project=project)
                for tknotice in tknotices:
                    tknotice.communities.add(community)
                    tknotice.message = message
                    tknotice.save()
        
        return redirect('institution-projects', institution.id)

    context = {
        'institution': institution,
        'project': project,
        'contribs': contribs,
        'communities': communities,
    }
    return render(request, 'institutions/notify.html', context)


