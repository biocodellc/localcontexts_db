from researchers.models import Researcher
from institutions.models import Institution
from notifications.models import ActionNotification
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

            if project_status == 'pending':
                status.status = 'pending'
                title = f'{community.community_name} is in the process of applying Labels to your Project: {truncated_project_title}'

            if project_status == 'not_pending':
                status.status = 'not_pending'
                title = f'{community.community_name} will not be applying Labels to your Project: {truncated_project_title}'

            status.save()

            # Send Notification
            if creator.institution:
                send_simple_action_notification(user, creator.institution, title, 'Projects', reference_id)
            if creator.researcher:
                send_simple_action_notification(user, creator.researcher, title, 'Projects', reference_id)

def project_status_seen_at_comment(user, community, creator, project):
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


def add_to_contributors(request, contributors, institutions_list, researchers_list, project_id):
    # Add each institution and researcher to contributors
    if institutions_list:
        for institution_id in institutions_list:
            institution = Institution.objects.select_related('institution_creator').get(id=institution_id)
            contributors.institutions.add(institution)

            # create notification
            send_simple_action_notification(None, institution, 'Your institution has been added as a contributor on a Project', 'Projects', project_id)
            # create email
            send_contributor_email(request, institution, project_id)

    if researchers_list:
        for researcher_id in researchers_list:
            researcher = Researcher.objects.get(id=researcher_id)
            contributors.researchers.add(researcher)

            # create notification
            send_simple_action_notification(None, researcher, 'You have been added as a contributor on a Project', 'Projects', project_id)
            # create email
            send_contributor_email(request, researcher, project_id)
