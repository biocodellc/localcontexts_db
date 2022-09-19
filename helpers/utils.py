import json
import requests
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
from .models import Connections, Notice
from notifications.models import *

from helpers.emails import send_membership_email

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

def accepted_join_request(org, join_request_id, selected_role):
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

            # Delete join request
            join_request.delete()


def set_language_code(instance):
    url = 'https://raw.githubusercontent.com/biocodellc/localcontexts_json/main/data/ianaObj.json'
    data = requests.get(url).json()

    if instance.language in data.keys():
        instance.language_tag = data[instance.language]
        instance.save()


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

def add_to_connections(target_org, org):

    if isinstance(target_org, Community):
        connections = Connections.objects.get(community=target_org)
        if isinstance(org, Institution):
            connections.institutions.add(org)
        if isinstance(org, Researcher):
            connections.researchers.add(org)
        connections.save()

    if isinstance(target_org, Institution):
        connections = Connections.objects.get(institution=target_org)
        if isinstance(org, Community):
            connections.communities.add(org)
        connections.save()

    if isinstance(target_org, Researcher):
        connections = Connections.objects.get(researcher=target_org)
        if isinstance(org, Community):
            connections.communities.add(org)
        connections.save() 

# Create/Update Notices
def create_notices(selected_notices, organization, project, existing_notices):
    # organization: either instance of institution or researcher
    # selected_notices would be a list: # attribution_incomplete # bcnotice # tknotice
    if existing_notices:
        for notice in existing_notices:
            notice.delete()

    for selected in selected_notices:
        notice_type = ''
        if selected == 'bcnotice':
            notice_type = 'biocultural'
        elif selected == 'tknotice':
            notice_type='traditional_knowledge'
        elif selected == 'attribution_incomplete':
            notice_type='attribution_incomplete'

        if isinstance(organization, Institution):
            Notice.objects.create(notice_type=notice_type, institution=organization, project=project)

        if isinstance(organization, Researcher):
            Notice.objects.create(notice_type=notice_type, researcher=organization, project=project)


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