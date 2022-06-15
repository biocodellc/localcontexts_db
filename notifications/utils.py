from .models import ActionNotification
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher

def send_simple_action_notification(sender, target_org, title, type, reference_id):
    if isinstance(target_org, Community):
        ActionNotification.objects.create(sender=sender, community=target_org, notification_type=type, title=title, reference_id=reference_id)
    elif isinstance(target_org, Institution):
        ActionNotification.objects.create(sender=sender, institution=target_org, notification_type=type, title=title, reference_id=reference_id)
    elif isinstance(target_org, Researcher):
        ActionNotification.objects.create(sender=sender, researcher=target_org, notification_type=type, title=title, reference_id=reference_id)