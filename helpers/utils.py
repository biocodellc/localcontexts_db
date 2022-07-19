import json
import requests
import zipfile
from django.template.loader import get_template
from io import BytesIO
from accounts.models import UserAffiliation
from xhtml2pdf import pisa

from communities.models import Community, JoinRequest, InviteMember
from institutions.models import Institution
from researchers.models import Researcher
from .models import Connections, Notice
from notifications.models import *

from helpers.emails import send_membership_email

def is_organization_in_user_affiliation(user, organization):
    affiliation = UserAffiliation.objects.prefetch_related('communities').get(user=user)
    if isinstance(organization, Community):
        if organization in affiliation.communities.all():
            return True
        else:
            return False
            
    if isinstance(organization, Institution):
        if organization in affiliation.institutions.all():
            return True
        else:
            return False

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

def get_notices_json():
    json_data = open('./localcontexts/static/json/Notices.json')
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

def set_notice_defaults(notice):
    data = get_notices_json()
    baseURL = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/'

    for item in data:
        if item['noticeType'] == notice.notice_type:
            notice.name = item['noticeName']
            notice.img_url = baseURL + item['imgFileName']
            notice.svg_url = baseURL + item['svgFileName']
            notice.default_text = item['noticeDefaultText']
    notice.save()  

# Helper function for creating/updating notices
def loop_through_notices(list, organization, project):
    for selected in list:
        if isinstance(organization, Institution):
            if selected == 'bcnotice':
                notice = Notice.objects.create(notice_type='biocultural', institution=organization, project=project)
            elif selected == 'tknotice':
                notice = Notice.objects.create(notice_type='traditional_knowledge', institution=organization, project=project)
            elif selected == 'attribution_incomplete':
                notice = Notice.objects.create(notice_type='attribution_incomplete', institution=organization, project=project)

        if isinstance(organization, Researcher):
            if selected == 'bcnotice':
                notice = Notice.objects.create(notice_type='biocultural', researcher=organization, project=project)
            elif selected == 'tknotice':
                notice = Notice.objects.create(notice_type='traditional_knowledge', researcher=organization, project=project)
            elif selected == 'attribution_incomplete':
                notice = Notice.objects.create(notice_type='attribution_incomplete', researcher=organization, project=project)
        
        set_notice_defaults(notice)


# Create/Update Notices
def create_notices(selected_notices, organization, project, existing_notice):
    # organization: either instance of institution or researcher
    # selected_notices would be a list: # attribution_incomplete # bcnotice # tknotice
    
    if existing_notice:
        existing_notice.delete()
    
    loop_through_notices(selected_notices, organization, project)
