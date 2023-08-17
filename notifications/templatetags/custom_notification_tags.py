from django import template
from notifications.models import UserNotification, ActionNotification
from django.contrib.auth.models import User
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher

register = template.Library()

@register.simple_tag
def unread_notifications_exist(account):
    if account is not None:
        if isinstance(account, User):
            return UserNotification.objects.filter(to_user=account, viewed=False).exists()

        if isinstance(account, Researcher):
            return ActionNotification.objects.filter(researcher=account, viewed=False).exists()

        if isinstance(account, Institution):
            return ActionNotification.objects.filter(institution=account, viewed=False).exists()

        if isinstance(account, Community):
            return ActionNotification.objects.filter(community=account, viewed=False).exists()
    
        return False

@register.simple_tag
def return_notifications(account):
    if account is not None:
        if isinstance(account, User):
            return UserNotification.objects.filter(to_user=account)

        if isinstance(account, Researcher):
            return ActionNotification.objects.filter(researcher=account)

        if isinstance(account, Institution):
            return ActionNotification.objects.filter(institution=account)

        if isinstance(account, Community):
            return ActionNotification.objects.filter(community=account)
        
        return None
    