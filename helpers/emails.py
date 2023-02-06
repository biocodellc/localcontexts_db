from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from .models import LabelNote
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from projects.models import Project
from django.contrib.auth.models import User

from localcontexts.utils import dev_prod_or_local
from accounts.utils import get_users_name

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
import requests
import re
import json

from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenGenerator(PasswordResetTokenGenerator):
    pass

generate_token=TokenGenerator()

# MAILGUN TEMPLATES
def add_template(filename, temp_name, description):
    template = render_to_string(f'snippets/emails/{filename}.html')
    return requests.post(
        settings.MAILGUN_TEMPLATE_URL,
        auth=("api", settings.MAILGUN_API_KEY),
        data={'template': template,
              'name': temp_name,
              'description': description})

def send_mailgun_template_email(email, subject, template_name, data):

    return requests.post(
        settings.MAILGUN_BASE_URL,
        auth=("api", settings.MAILGUN_API_KEY),
        data={
            "from": "Local Contexts Hub <no-reply@localcontextshub.org>",
            "to": email,
            "subject": subject,
            "template": template_name,
            "t:variables": json.dumps(data)
            })

def is_valid_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

# Send simple email no attachments
def send_simple_email(to_emails, subject, template):
    # to_emails can be a string or list of emails
    def send(email):
        return requests.post(
            settings.MAILGUN_BASE_URL,
            auth=("api", settings.MAILGUN_API_KEY),
            data={"from": "Local Contexts Hub <no-reply@localcontextshub.org>",
                "to": [email],
                "subject": subject,
                "html": template}
        )
    
    if isinstance(to_emails, str):
        if is_valid_email(to_emails):
            send(to_emails)
    elif isinstance(to_emails, list):
        for address in to_emails:
            if is_valid_email(address):
                    send(address)
    else:
        pass

# Send email with attachment
def send_email_with_attachment(file, to_email, subject, template):
    return requests.post(
        settings.MAILGUN_BASE_URL,
        auth=("api", settings.MAILGUN_API_KEY),
        files=[("attachment", (file.name, file.read())),],
        data={"from": "Local Contexts Hub <no-reply@localcontextshub.org>",
              "to": to_email,
            #   "bcc": "bar@example.com",
              "subject": subject,
              "html": template})

def send_update_email(email):
    template = render_to_string('snippets/emails/hub-updates.html')
    send_simple_email(email, 'Local Contexts Hub Updates', template)

# Send all Institution and community applications to support or the site admin
def send_hub_admins_application_email(request, organization, data):
    template = ''
    subject = ''

    if isinstance(organization, Community):
        subject = f'New Community Application: {data.community_name}'
        template = render_to_string('snippets/emails/community-application.html', { 'data' : data })
    else: 
        if data.is_ror:
            subject = f'New Institution Application: {data.institution_name}'
        else:
            subject = f'New Institution Application (non-ROR): {data.institution_name}'

        template = render_to_string('snippets/emails/institution-application.html', { 'data' : data })


    # if admin group exists:
    if dev_prod_or_local(request.get_host()) == 'PROD':
        emails = [settings.SITE_ADMIN_EMAIL, 'support@localcontexts.org']
        
        # If file, send as attachment
        if data.support_document:
            send_email_with_attachment(data.support_document, emails, subject, template)
        else:
            send_simple_email(emails, subject, template)
    else:
        # Send to site admin only (will be typically for testing)
        if data.support_document:
            send_email_with_attachment(data.support_document, settings.SITE_ADMIN_EMAIL, subject, template)
        else:
            send_simple_email(settings.SITE_ADMIN_EMAIL, subject, template)

"""
    EMAILS FOR ACCOUNTS APP
"""

# Registration: User Activation email
def send_activation_email(request, user):
    # Remember the current location
    current_site=get_current_site(request)
    domain = current_site.domain
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = generate_token.make_token(user)

    if 'localhost' in domain:
        activation_url = f'http://{domain}/activate/{uid}/{token}'
    else:
        activation_url = f'https://{domain}/activate/{uid}/{token}'

    data = {'user': user.username, 'activation_url': activation_url}
    subject = 'Activate Your Local Contexts Hub Profile'
    send_mailgun_template_email(user.email, subject, 'activate_profile', data)

#  Resend Activation Email
def resend_activation_email(request, active_users):
    to_email= active_users[0].email
    current_site=get_current_site(request)
    domain = current_site.domain
    uid = urlsafe_base64_encode(force_bytes(active_users[0].pk))
    token = generate_token.make_token(active_users[0])
    user = active_users[0].username

    if 'localhost' in domain:
        activation_url = f'http://{domain}/activate/{uid}/{token}'
    else:
        activation_url = f'https://{domain}/activate/{uid}/{token}'

    data = {'user': user, 'activation_url': activation_url}
    subject = 'Activate Your Local Contexts Hub Profile'
    send_mailgun_template_email(to_email, subject, 'activate_profile', data)


# User has activated account and has logged in: Welcome email
def send_welcome_email(request, user):   
    current_site=get_current_site(request)
    subject = 'Welcome to Local Contexts Hub!'
    domain = current_site.domain

    if 'localhost' in domain:
        url = f'http://{domain}/login'
    else:
        url = f'https://{domain}/login'

    send_mailgun_template_email(user.email, subject, 'welcome', {"login_url": url})

# TEST THIS
# Email to invite user to join the hub
def send_invite_user_email(request, data):
    current_site=get_current_site(request)
    subject = 'You have been invited to join the Local Contexts Hub'
    name = get_users_name(data.sender)
    domain = current_site.domain

    if 'localhost' in domain:
        url = f'http://{domain}/register'
    else:
        url = f'https://{domain}/register'

    variables = {"register_url": url, "name": name, "message": data.message}
    send_mailgun_template_email(data.email, subject, 'invite_new_user', variables)

# Anywhere JoinRequest instance is created, 
# will email community or institution creator that someone wants to join the organization
def send_join_request_email_admin(request, join_request, organization):
    current_site=get_current_site(request)
    name = get_users_name(request.user)
    domain = current_site.domain

    if 'localhost' in domain:
        login_url = f'http://{domain}/login'
    else:
        login_url = f'https://{domain}/login'

    # Check if organization instance is community model
    if isinstance(organization, Community):
        subject = f'{name} has requested to join {organization.community_name}'
        send_to_email = organization.community_creator.email
        org_name = organization.community_name
    if isinstance(organization, Institution):
        subject = f'{name} has requested to join {organization.institution_name}'
        send_to_email = organization.institution_creator.email
        org_name = organization.institution_name

    data = { 
            'user': name, 
            'org_name': org_name,
            'message': join_request.message,
            'role': join_request.role,
            'login_url': login_url
        }
    
    send_mailgun_template_email(send_to_email, subject, 'join_request', data)

"""
    EMAILS FOR INSTITUTION APP
"""

def send_institution_invite_email(request, data, institution):
    current_site=get_current_site(request)
    template = render_to_string('snippets/emails/member-invite.html', { 
        'domain':current_site.domain,
        'data': data, 
        'institution': institution 
    })
    title = f'You have been invited to join {institution.institution_name}'
    send_simple_email(data.receiver.email, title, template)

# A notice has been applied by researcher or institution
def send_email_notice_placed(project, community, sender):
    # Can pass instance of institution or researcher as sender
    template = render_to_string('snippets/emails/notice-placed.html', { 'project': project, 'sender': sender, })
    title = ''
    if isinstance(sender, Institution):
        title = f'{sender.institution_name} has placed a Notice'
    if isinstance(sender, Researcher):
        name = get_users_name(sender.user)
        title = f'{name} has placed a Notice'
    
    send_simple_email(community.community_creator.email, title, template)
    

"""
    EMAILS FOR COMMUNITY APP
"""

# Inviting a user to join community
def send_community_invite_email(request, data, community):
    current_site=get_current_site(request)
    template = render_to_string('snippets/emails/member-invite.html', { 
        'domain':current_site.domain,
        'data': data, 
        'community': community 
    })
    send_simple_email(data.receiver.email, 'You have been invited to join a community', template)

# When Labels have been applied to a Project
def send_email_labels_applied(project, community):
    template = render_to_string('snippets/emails/labels-applied.html', { 'project': project, 'community': community, })
    send_simple_email(project.project_creator.email, 'A community has applied Labels to your Project', template)

# Label has been approved or not
def send_email_label_approved(label):
    label_notes = LabelNote.objects.none()
    if isinstance(label, BCLabel):
        label_notes = LabelNote.objects.filter(bclabel=label)
    if isinstance(label, TKLabel):
        label_notes = LabelNote.objects.filter(tklabel=label)

    template = render_to_string('snippets/emails/label-approved.html', { 'label': label, 'label_notes': label_notes })

    if label.is_approved:
        send_simple_email(label.created_by.email, 'Your Label has been approved', template)
    else:
        send_simple_email(label.created_by.email, 'Your Label has not been approved', template)

# You are now a member of institution/community email
def send_membership_email(request, organization, receiver, role):
    current_site=get_current_site(request)

    template = render_to_string('snippets/emails/membership-info.html', { 
        'domain':current_site.domain,
        'organization': organization, 
        'role': role, 
    })
    title = ''
    if isinstance(organization, Community):
        title = f'You are now a member of {organization.community_name}'
    if isinstance(organization, Institution):
        title = f'You are now a member of {organization.institution_name}'

    send_simple_email(receiver.email, title, template)

# Send email to support when a Researcher connects to the Hub in PRODUCTION
def send_email_to_support(researcher):
    template = render_to_string('snippets/emails/researcher-account-connection.html', { 'researcher': researcher })
    name = get_users_name(researcher.user)
    title = f'{name} has created a Researcher Account'
    send_simple_email('support@localcontexts.org', title, template)  


# REGISTRY Contact organization email
def send_contact_email(to_email, from_name, from_email, message):
    subject = f"{from_name} has sent you a message from the Local Contexts Hub"
    from_string = f"{from_name} <{from_email}>"
    template = render_to_string('snippets/emails/registry-contact.html', { 'from_name': from_name, 'message': message, })

    return requests.post(
		settings.MAILGUN_BASE_URL,
		auth=("api", settings.MAILGUN_API_KEY),
		data={"from": from_string,
			"to": [to_email],
			# "bcc": [to_email],
			"subject": subject,
            "html": template}
    )

def send_contributor_email(request, org, proj_id):
    current_site=get_current_site(request)
    to_email = ''
    subject = ''
    project = Project.objects.select_related('project_creator').get(unique_id=proj_id)

    if '/create-project/' in request.path:
        template = render_to_string('snippets/emails/contributor.html', { 'domain': current_site.domain, 'project': project, 'create': True })
        
        if isinstance(org, Community):
            to_email = org.community_creator.email
            subject = "Your community has been added as a contributor on a Project"
        if isinstance(org, Institution):
            to_email = org.institution_creator.email
            subject = "Your institution has been added as a contributor on a Project"
        if isinstance(org, Researcher):
            to_email = org.user.email
            subject = "You have been added as a contributor on a Project"

    elif '/edit-project/' in request.path:
        template = render_to_string('snippets/emails/contributor.html', { 'domain': current_site.domain, 'project': project, 'edit': True })
        subject = "Changes have been made to a Project you're contributing to"
        
        if isinstance(org, Community):
            to_email = org.community_creator.email
        if isinstance(org, Institution):
            to_email = org.institution_creator.email
        if isinstance(org, Researcher):
            to_email = org.user.email

    send_simple_email(to_email, subject, template)

def send_project_person_email(request, to_email, proj_id):
    current_site=get_current_site(request)
    registered = User.objects.filter(email=to_email).exists()

    project_person = True
    project = Project.objects.select_related('project_creator').get(unique_id=proj_id)
    subject = 'You have been added as a contributor on a Local Contexts Hub Project'
    template = render_to_string('snippets/emails/contributor.html', { 
        'domain':current_site.domain,
        'project': project, 
        'project_person': project_person, 
        'registered': registered,
    })
    send_simple_email(to_email, subject, template)
