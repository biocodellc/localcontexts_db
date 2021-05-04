from django import template
from django.urls import reverse
from notifications.models import InstitutionNotification

register = template.Library()

@register.simple_tag
def institution_notifications(institution):
    notifications = InstitutionNotification.objects.filter(institution=institution)
    return notifications

@register.simple_tag
def anchor(url_name, section_id, institution_id):
    return reverse(url_name, kwargs={'pk': institution_id}) + "#full-notice-card-" + str(section_id)
