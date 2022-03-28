from django import template
from communities.models import JoinRequest

register = template.Library()

@register.simple_tag
def display_joinrequest_message(reference_id):
    join_request = JoinRequest.objects.filter(id=reference_id)
    if join_request.exists():
        return JoinRequest.objects.get(id=reference_id).message
