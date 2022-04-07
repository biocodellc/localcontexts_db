from django import template
from communities.models import JoinRequest
from notifications.models import UserNotification
from accounts.utils import get_users_name

register = template.Library()

@register.simple_tag
def join_request_inst(institution, user):
    request_exists = JoinRequest.objects.filter(institution=institution, user_from=user).exists()
    return request_exists

@register.simple_tag
def join_request_comm(community, user):
    request_exists = JoinRequest.objects.filter(community=community, user_from=user).exists()
    return request_exists

@register.simple_tag
def unread_notifications_exist(user):
    return UserNotification.objects.filter(to_user=user, viewed=False).exists()

@register.simple_tag
def display_name(user):
    return get_users_name(user)