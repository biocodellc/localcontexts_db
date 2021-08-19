from researchers.models import Researcher
from institutions.models import Institution
from .models import ProjectContributors

def add_to_contributors(contributors, project, institutions_list, researchers_list):
    # Add each institution and researcher to contributors
    if institutions_list:
        for institution_id in institutions_list:
            inst = Institution.objects.get(id=institution_id)
            contributors.institutions.add(inst)
    if researchers_list:
        for researcher_id in researchers_list:
            res = Researcher.objects.get(id=researcher_id)
            contributors.researchers.add(res)

def set_project_privacy(project, privacy_level):
    if privacy_level == 'public':
        project.project_privacy = 'Public'
    if privacy_level == 'discoverable':
        project.project_privacy = 'Discoverable'
    if privacy_level == 'private':
        project.project_privacy = 'Private'
        return project
