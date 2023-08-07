import json
import zipfile
from django.template.loader import get_template
from io import BytesIO
from accounts.models import UserAffiliation
from tklabels.models import TKLabel
from bclabels.models import BCLabel
from helpers.models import LabelTranslation, LabelVersion, LabelTranslationVersion
from xhtml2pdf import pisa

from communities.models import Community, JoinRequest, InviteMember
from institutions.models import Institution
from researchers.models import Researcher
from .models import Notice
from notifications.models import *

from accounts.utils import get_users_name
from helpers.emails import send_membership_email
from django.contrib.staticfiles import finders


def check_member_role(user, organization):
    role = ''
    if isinstance(organization, Community):
        if user == organization.community_creator:
            return 'admin'

    if isinstance(organization, Institution):
        if user == organization.institution_creator:
            return 'admin'
    
    if user in organization.admins.all():
        role = 'admin'
    elif user in organization.editors.all():
        role = 'editor'
    elif user in organization.viewers.all():
        role = 'viewer'
    else:
        return False
    
    return role
    
def accept_member_invite(request, invite_id):
    invite = InviteMember.objects.get(id=invite_id)
    affiliation = UserAffiliation.objects.get(user=invite.receiver)

    # Which organization, add yto user affiliation
    org = ''
    if invite.community:
        org = invite.community
        affiliation.communities.add(org)

    if invite.institution:
        org = invite.institution
        affiliation.institutions.add(org)
    
    affiliation.save()
    
    # Add user to role
    if invite.role == 'viewer':
        org.viewers.add(invite.receiver)
    elif invite.role == 'admin':
        org.admins.add(invite.receiver)
    elif invite.role == 'editor':
        org.editors.add(invite.receiver)
    
    org.save()

    # Send email letting user know they are a member
    send_membership_email(request, org, invite.receiver, invite.role)

    # Find relevant user notification to delete
    if UserNotification.objects.filter(to_user=invite.receiver, from_user=invite.sender, reference_id=invite.id).exists():
        notification = UserNotification.objects.get(to_user=invite.receiver, from_user=invite.sender, reference_id=invite.id)
        notification.delete()

    # Delete invitation
    invite.delete()

def change_member_role(org, member, current_role, new_role):
    if new_role is None:
        pass
    else:
        # Remove user from previous role
        if current_role == 'admin':
            org.admins.remove(member)
        elif current_role == 'editor':
            org.editors.remove(member)
        elif current_role == 'viewer':
            org.viewers.remove(member)
        
        # Add user to new role
        if new_role == 'Administrator':
            org.admins.add(member)
        elif new_role == 'Editor':
            org.editors.add(member)
        elif new_role == 'Viewer':
            org.viewers.add(member)

def accepted_join_request(request, org, join_request_id, selected_role):
    # Passes instance of Community or Institution, a join_request pk, and a selected role
    if JoinRequest.objects.filter(id=join_request_id).exists():
        join_request = JoinRequest.objects.get(id=join_request_id)
        if selected_role is None:
            pass
        else:
            # Add organization to userAffiliation and delete relevant action notification
            affiliation = UserAffiliation.objects.get(user=join_request.user_from)
            if isinstance(org, Community):
                affiliation.communities.add(org)
                if ActionNotification.objects.filter(sender=join_request.user_from, community=org, reference_id=join_request.id).exists():
                    notification = ActionNotification.objects.get(sender=join_request.user_from, community=org, reference_id=join_request.id)
                    notification.delete()
            if isinstance(org, Institution):
                affiliation.institutions.add(org)
                if ActionNotification.objects.filter(sender=join_request.user_from, institution=org, reference_id=join_request.id).exists():
                    notification = ActionNotification.objects.get(sender=join_request.user_from, institution=org, reference_id=join_request.id)
                    notification.delete()

            # Add member to role
            if selected_role == 'Administrator':
                org.admins.add(join_request.user_from)
            elif selected_role == 'Editor':
                org.editors.add(join_request.user_from)
            elif selected_role == 'Viewer':
                org.viewers.add(join_request.user_from)
            
            # Create UserNotification
            sender = join_request.user_from
            title = f"You are now a member of {org}!"
            UserNotification.objects.create(to_user=sender, title=title, notification_type="Accept")

            send_membership_email(request, org, sender, selected_role)

            # Delete join request
            join_request.delete()

# h/t: https://stackoverflow.com/questions/59695870/generate-multiple-pdfs-and-zip-them-for-download-all-in-a-single-view
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    buffer = BytesIO()
    p = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), buffer)
    pdf = buffer.getvalue()
    buffer.close()
    if not p.err:
        return pdf
    return None

def generate_zip(files):
    mem_zip = BytesIO()

    with zipfile.ZipFile(mem_zip, mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.writestr(f[0], f[1])

    return mem_zip.getvalue()

def get_labels_json():
    json_data = open('./localcontexts/static/json/Labels.json')
    data = json.load(json_data) #deserialize
    return data

def get_collections_care_notices():
    json_path = finders.find('json/CollectionsCareNotices.json')
    with open(json_path, 'r') as file:
        data = json.load(file)
    return data

def get_notice_translations():
    json_path = finders.find('json/NoticeTranslations.json')
    with open(json_path, 'r') as file:
        data = json.load(file)
    
    # Restructure the data as a nested dictionary with noticeType and language as keys
    notice_translations = {}
    for item in data:
        notice_type = item['noticeType']
        language_tag = item['languageTag']
        if notice_type not in notice_translations:
            notice_translations[notice_type] = {}
        notice_translations[notice_type][language_tag] = item
    return notice_translations

def get_notice_defaults():
    json_path = finders.find('json/Notices.json')
    with open(json_path, 'r') as file:
        data = json.load(file)
    return data

# Create/Update/Delete Notices and Notice Translations
def crud_notices(request, selected_notices, selected_translations, organization, project, existing_notices):
    # organization: instance of institution or researcher
    # selected_notices: list: ['attribution_incomplete', 'bcnotice', 'tknotice']
    # existing_notices: a queryset of notices that exist for this project already
    # selected_translations: list: ['traditional_knowledge-fr', 'biocultural-es'], etc.

    from projects.models import ProjectActivity
    name = get_users_name(request.user)

    def create(notice_type):
        if isinstance(organization, (Institution, Researcher)):
            notice_fields = {
                'notice_type': notice_type,
                'project': project,
            }

            if isinstance(organization, Institution):
                notice_fields['institution'] = organization
            elif isinstance(organization, Researcher):
                notice_fields['researcher'] = organization

            new_notice = Notice.objects.create(**notice_fields)
            ProjectActivity.objects.create(project=project, activity=f'{new_notice.name} was applied to the Project by {name}')

            # Create any notice translations
            update_notice_translation(new_notice, selected_translations)

    def create_notices(existing_notice_types):          
        for notice_type in selected_notices:
            if notice_type:
                if existing_notice_types:
                    if not notice_type in existing_notice_types:  
                        create(notice_type)
                else:
                    create(notice_type)
    
    def update_notice_translation(notice, selected_translations):
        if selected_translations:
            for value in selected_translations:
                ntype, lang_tag = value.split('-')

                # If translation of this type in this language does NOT exist, create it.
                if not notice.notice_translations.filter(notice_type=ntype, language_tag=lang_tag).exists():
                    notice.save(language_tag=lang_tag)

                # If other translations exist that are not on the list, delete them
                elif notice.notice_translations.exclude(notice_type=ntype, language_tag=lang_tag).exists():
                    translations_to_delete = notice.notice_translations.exclude(notice_type=ntype, language_tag=lang_tag)
                    for item in translations_to_delete:
                        item.delete()
                
    if existing_notices:
        existing_notice_types = []
        for notice in existing_notices:
            existing_notice_types.append(notice.notice_type)
            if not notice.notice_type in selected_notices: # if existing notice not in selected notices, delete notice
                notice.delete()
                ProjectActivity.objects.create(project=project, activity=f'{notice.name} was removed from the Project by {name}')
            update_notice_translation(notice, selected_translations)
        create_notices(existing_notice_types)

    else:
        create_notices(None)

def add_remove_labels(request, project, community):
    from projects.models import ProjectActivity
    # Get uuids of each label that was checked and add them to the project
    bclabels_selected = request.POST.getlist('selected_bclabels')
    tklabels_selected = request.POST.getlist('selected_tklabels')

    bclabels = BCLabel.objects.filter(unique_id__in=bclabels_selected)
    tklabels = TKLabel.objects.filter(unique_id__in=tklabels_selected)

    user = get_users_name(request.user)

    # find target community labels and clear those only!
    if project.bc_labels.filter(community=community).exists():

        for bclabel in project.bc_labels.filter(community=community).exclude(unique_id__in=bclabels_selected): # does project have labels from this community that aren't the selected ones?
            project.bc_labels.remove(bclabel) 
            ProjectActivity.objects.create(project=project, activity=f'{bclabel.name} Label was removed by {user} | {community.community_name}')

    if project.tk_labels.filter(community=community).exists():
        for tklabel in project.tk_labels.filter(community=community).exclude(unique_id__in=tklabels_selected):
            project.tk_labels.remove(tklabel)
            ProjectActivity.objects.create(project=project, activity=f'{tklabel.name} Label was removed by {user} | {community.community_name}')

    for bclabel in bclabels:
        if not bclabel in project.bc_labels.all(): # if label not in project labels, apply it
            project.bc_labels.add(bclabel)
            ProjectActivity.objects.create(project=project, activity=f'{bclabel.name} Label was applied by {user} | {community.community_name}')

    for tklabel in tklabels:
        if not tklabel in project.tk_labels.all():
            project.tk_labels.add(tklabel)
            ProjectActivity.objects.create(project=project, activity=f'{tklabel.name} Label was applied by {user} | {community.community_name}')
    
    project.save()


def handle_label_versions(label):
    # passes instance of BCLabel or TKLabel
    version = LabelVersion.objects.none()
    translations = LabelTranslation.objects.none()
    version_num = 0

    if isinstance(label, BCLabel):
        translations = LabelTranslation.objects.filter(bclabel=label)

        # If approved version exists, set version number to 1 more than the latest
        latest_version = LabelVersion.objects.filter(bclabel=label).order_by('-version').first()

        if latest_version is not None:
            if latest_version.is_approved:
                version_num = latest_version.version + 1
            elif not latest_version.is_approved:
                latest_version.is_approved = True
                latest_version.save()
        else:
            version_num = 1
            label.version = 1
            label.save()

        # Create Version for BC Label
        version = LabelVersion.objects.create(
            bclabel=label,
            version=version_num, 
            created_by=label.created_by, 
            is_approved=True,
            approved_by=label.approved_by,
            version_text=label.label_text,
            created=label.created
        )

    if isinstance(label, TKLabel):
        translations = LabelTranslation.objects.filter(tklabel=label)

        # If approved version exists, set version number to 1 more than the latest
        latest_version = LabelVersion.objects.filter(tklabel=label).order_by('-version').first()

        if latest_version is not None:
            if latest_version.is_approved:
                version_num = latest_version.version + 1
            elif not latest_version.is_approved:
                latest_version.is_approved = True
                latest_version.save()
        else:
            version_num = 1
            label.version = 1
            label.save()

        # Create Version for TK Label
        version = LabelVersion.objects.create(
            tklabel=label,
            version=version_num, 
            created_by=label.created_by, 
            is_approved=True,
            approved_by=label.approved_by,
            version_text=label.label_text,
            created=label.created
        )

    # Create version translations
    for t in translations:
        LabelTranslationVersion.objects.create(
            version_instance=version,
            translated_name=t.translated_name,
            language=t.language, 
            language_tag=t.language_tag,
            translated_text=t.translated_text,
            created=version.created
        )

def discoverable_project_view(project, user):
    project_contributors = project.project_contributors
    creator_account = project.project_creator_project.first()
    is_created_by = creator_account.which_account_type_created()
    notified = project.project_notified.first()

    discoverable = 'partial'

    if not user.is_authenticated:
        discoverable = 'partial'
    elif creator_account.is_user_in_creator_account(user, is_created_by):
        discoverable = True
    elif project_contributors.is_user_contributor(user):
        discoverable = True
    elif notified.is_user_in_notified_account(user):
        discoverable = True
    else:
        discoverable = False

    return discoverable

def set_ror_id(institution):
    import requests

    url = 'https://api.ror.org/organizations'
    query = institution.institution_name
    params = { 'query': query }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            ror_id = data['items'][0]['id']
            institution.ror_id = ror_id
            institution.save()
        else:
            print('No matching institution found.')
    else:
        print('Error:', response.status_code)
