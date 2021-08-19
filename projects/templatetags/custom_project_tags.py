from django import template
from institutions.models import Institution
from researchers.models import Researcher
from communities.models import Community
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

# TODO: what if there are 2 notices?
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

def discoverable_project(user, project):
    # Is user in..
    # If project privacy is discoverable...
    # Notified Communities
    # placed_by_institution
    # placed_by_researcher
    # project creator
    # If status exists
    
    return True