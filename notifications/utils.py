from .models import ActionNotification
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from projects.models import ProjectContributors

def send_simple_action_notification(sender, target_org, title, type, reference_id):
    if isinstance(target_org, Community):
        ActionNotification.objects.create(sender=sender, community=target_org, notification_type=type, title=title, reference_id=reference_id)
    elif isinstance(target_org, Institution):
        ActionNotification.objects.create(sender=sender, institution=target_org, notification_type=type, title=title, reference_id=reference_id)
    elif isinstance(target_org, Researcher):
        ActionNotification.objects.create(sender=sender, researcher=target_org, notification_type=type, title=title, reference_id=reference_id)

def send_action_notification_to_project_contribs(project):
    contrib = ProjectContributors.objects.prefetch_related('communities', 'institutions', 'researchers').get(project=project)
    if contrib.communities:
        for community in contrib.communities.all():
            send_simple_action_notification(None, community, 'Project has a new message', 'Projects', project.unique_id)
    if contrib.institutions.all():
        for institution in contrib.institutions.all():
            send_simple_action_notification(None, institution, 'Project has a new message', 'Projects', project.unique_id)
    if contrib.researchers.all():
        for researcher in contrib.researchers.all():
            send_simple_action_notification(None, researcher, 'Project has a new message', 'Projects', project.unique_id)
