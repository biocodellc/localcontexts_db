from researchers.models import Researcher
from institutions.models import Institution
from communities.models import Community
from projects.models import ProjectContributors, ProjectActivity
from helpers.emails import send_contributor_email
from notifications.utils import send_simple_action_notification
from helpers.models import ProjectStatus

def set_project_status(user, project, community, creator, project_status):
        truncated_project_title = str(project.title)[0:30]
        reference_id = project.unique_id

        statuses = ProjectStatus.objects.filter(project=project, community=community)

        title = ''
        for status in statuses:
            status.seen = True

            if project_status == 'seen':
                title = f'{community.community_name} has seen and acknowledged your Project: {truncated_project_title}'
                ProjectActivity.objects.create(project=project, activity=f'{community.community_name} set the Project status to Seen')

            if project_status == 'pending':
                status.status = 'pending'
                title = f'{community.community_name} is in the process of applying Labels to your Project: {truncated_project_title}'
                ProjectActivity.objects.create(project=project, activity=f'{community.community_name} set the Project status to Labels Pending')

            if project_status == 'not_pending':
                status.status = 'not_pending'
                title = f'{community.community_name} will not be applying Labels to your Project: {truncated_project_title}'
                ProjectActivity.objects.create(project=project, activity=f'{community.community_name} set the Project status to No Labels Pending')

            status.save()

            # Send Notification
            if creator.institution:
                send_simple_action_notification(user, creator.institution, title, 'Projects', reference_id)
            if creator.researcher:
                send_simple_action_notification(user, creator.researcher, title, 'Projects', reference_id)

def project_status_seen_at_comment(user, community, creator, project):
    if ProjectStatus.objects.filter(project=project, community=community).exists():
        status = ProjectStatus.objects.get(project=project, community=community)

        truncated_project_title = str(project.title)[0:30]
        reference_id = project.unique_id

        # If message is sent, set notice status to 'Seen'
        if status.seen == False:
            status.seen = True
            status.save()

            title = f'{community.community_name} has added a comment to your Project: {truncated_project_title}'

            # Send Notification
            if creator.institution:
                send_simple_action_notification(user, creator.institution, title, 'Projects', reference_id)
            if creator.researcher:
                send_simple_action_notification(user, creator.researcher, title, 'Projects', reference_id)


def add_to_contributors(request, account, project):
    contributors = ProjectContributors.objects.get(project=project)
    # Clear all contributors first
    contributors.communities.clear()
    contributors.institutions.clear()
    contributors.researchers.clear()

    if isinstance(account, Community):
        contributors.communities.add(account)
    if isinstance(account, Institution):
        contributors.institutions.add(account)
    if isinstance(account, Researcher):
        contributors.researchers.add(account)
    
    institutions_list = request.POST.getlist('selected_institutions')
    researchers_list = request.POST.getlist('selected_researchers')
    communities_list = request.POST.getlist('selected_communities')

    # Add each institution and researcher to contributors
    if institutions_list:
        for institution_id in institutions_list:
            institution = Institution.objects.select_related('institution_creator').get(id=institution_id)
            contributors.institutions.add(institution)

            if '/edit-project/' in request.path:
                send_simple_action_notification(None, institution, 'Edits have been made to a Project', 'Projects', project.unique_id)
            elif '/create-project/' in request.path:
                # create notification
                send_simple_action_notification(None, institution, 'Your institution has been added as a contributor on a Project', 'Projects', project.unique_id)
                # create email
            send_contributor_email(request, institution, project.unique_id)

    if researchers_list:
        for researcher_id in researchers_list:
            researcher = Researcher.objects.get(id=researcher_id)
            contributors.researchers.add(researcher)

            if '/edit-project/' in request.path:
                send_simple_action_notification(None, researcher, 'Edits have been made to a Project', 'Projects', project.unique_id)
            elif '/create-project/' in request.path:
                # create notification
                send_simple_action_notification(None, researcher, 'You have been added as a contributor on a Project', 'Projects', project.unique_id)
                # create email
            send_contributor_email(request, researcher, project.unique_id)
    
    if communities_list:
        for community_id in communities_list:
            community = Community.objects.select_related('community_creator').get(id=community_id)
            contributors.communities.add(community)

            if '/edit-project/' in request.path:
                send_simple_action_notification(None, community, 'Edits have been made to a Project', 'Projects', project.unique_id)
            elif '/create-project/' in request.path:
                # create notification
                send_simple_action_notification(None, community, 'Your community has been added as a contributor on a Project', 'Projects', project.unique_id)
                # create email
            send_contributor_email(request, community, project.unique_id)
