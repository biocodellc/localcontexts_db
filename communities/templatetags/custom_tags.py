from django import template
from django.urls import reverse
from bclabels.models import BCLabel
from tklabels.models import TKLabel

register = template.Library()

@register.simple_tag
def get_label_count(community):
    bclabels = BCLabel.objects.filter(community=community).count()
    tklabels = TKLabel.objects.filter(community=community).count()
    total_labels = bclabels + tklabels
    return total_labels

@register.simple_tag
def anchor(url_name, section_id, community_id):
    return reverse(url_name, kwargs={'pk': community_id}) + "#full-notice-card-" + str(section_id)