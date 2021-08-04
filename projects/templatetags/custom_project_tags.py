from django import template
from institutions.models import Institution
from researchers.models import Researcher
from helpers.models import NoticeStatus
from bclabels.models import BCNotice
from tklabels.models import TKNotice

register = template.Library()

@register.simple_tag
def get_all_researchers():
    return Researcher.objects.all()

@register.simple_tag
def get_all_institutions():
    return Institution.objects.all()

@register.simple_tag
def define(val=None):
    # To use: {% define 'oldVariable' as newVariable %}
  return val

@register.simple_tag
def which_communities_notified(project):
    if project.project_bcnotice.all().exists():
        bcnotice = BCNotice.objects.get(project=project)
        statuses = NoticeStatus.objects.filter(bcnotice=bcnotice)
        return statuses

    elif project.project_tknotice.all().exists():
        tknotice = TKNotice.objects.get(project=project)
        statuses = NoticeStatus.objects.filter(tknotice=tknotice)
        return statuses

    # if yes, 
    # check to see if notice status exists for a particular project then which community the status is associated with
