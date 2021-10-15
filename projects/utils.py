from researchers.models import Researcher
from institutions.models import Institution
from .models import ProjectContributors

def add_to_contributors(contributors, institutions_list, researchers_list):
    # print('***** INSTITUTIONS LIST ******')
    # print(institutions_list)
    # print('***** RESEARCHERS LIST ******')
    # print(researchers_list)
    
    # TODO: Remove researchers and institutions on edit
    # Add each institution and researcher to contributors
    if institutions_list:
        for institution_id in institutions_list:
            inst = Institution.objects.get(id=institution_id)
            contributors.institutions.add(inst)
    if researchers_list:
        for researcher_id in researchers_list:
            res = Researcher.objects.get(id=researcher_id)
            contributors.researchers.add(res)
