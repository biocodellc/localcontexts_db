from django import template
from institutions.models import Institution
from researchers.models import Researcher

register = template.Library()


@register.simple_tag
def get_all_researchers():
    return Researcher.objects.all()

@register.simple_tag
def get_all_institutions():
    return Institution.objects.all()