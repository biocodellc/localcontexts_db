from django import template
from communities.models import JoinRequest

register = template.Library()

@register.simple_tag
def display_joinrequest_message(reference_id):
    if JoinRequest.objects.filter(id=reference_id).exists():
        request = JoinRequest.objects.get(id=reference_id)
        return request.message
