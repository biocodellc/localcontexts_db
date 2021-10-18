from django import template
from communities.models import JoinRequest

register = template.Library()

@register.simple_tag
def join_request_inst(institution, user):
    request_exists = JoinRequest.objects.filter(institution=institution, user_from=user).exists()
    return request_exists

@register.simple_tag
def join_request_comm(community, user):
    request_exists = JoinRequest.objects.filter(community=community, user_from=user).exists()
    return request_exists
