from researchers.models import Researcher
from institutions.models import Institution
from notifications.models import ActionNotification
from helpers.emails import send_contributor_email

def add_to_contributors(contributors, institutions_list, researchers_list, project_id):
    # TODO: Remove researchers and institutions on edit

    # Add each institution and researcher to contributors
    if institutions_list:
        for institution_id in institutions_list:
            inst = Institution.objects.select_related('institution_creator').get(id=institution_id)
            contributors.institutions.add(inst)

            # create notification
            ActionNotification.objects.create(
                institution=inst, 
                notification_type='Projects',
                reference_id = project_id,
                title = 'Your institution has been added as a contributor on a Project'
            )
            # create email
            send_contributor_email(inst, project_id)

    if researchers_list:
        for researcher_id in researchers_list:
            res = Researcher.objects.get(id=researcher_id)
            contributors.researchers.add(res)

            # create notification
            ActionNotification.objects.create(
                researcher=res, 
                notification_type='Projects',
                reference_id = project_id,
                title = 'You have been added as a contributor on a Project'
            )
            # create email
            send_contributor_email(res, project_id)
