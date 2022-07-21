from django import template
from communities.models import Community, JoinRequest
from institutions.models import Institution
from notifications.models import UserNotification
from accounts.utils import get_users_name
from researchers.models import Researcher

register = template.Library()

@register.simple_tag
def community_count():
    return Community.approved.count()

@register.simple_tag
def institution_count():
    return Institution.approved.count()

@register.simple_tag
def researcher_count():
    return Researcher.objects.count()

@register.simple_tag
def join_request_inst(institution, user):
    return JoinRequest.objects.filter(institution=institution, user_from=user).exists()

@register.simple_tag
def join_request_comm(community, user):
    return JoinRequest.objects.filter(community=community, user_from=user).exists()

@register.simple_tag
def unread_notifications_exist(user):
    return UserNotification.objects.filter(to_user=user, viewed=False).exists()

@register.simple_tag
def display_name(user):
    return get_users_name(user)

@register.simple_tag
def is_user_member(account, user):
    if isinstance(account, Institution):
        return account.is_user_in_institution(user)
    if isinstance(account, Community):
        return account.is_user_in_community(user)