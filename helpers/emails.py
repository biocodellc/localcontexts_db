from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from django.contrib.auth.models import User
from helpers.models import LabelNote

from localcontexts.utils import dev_prod_or_local
from accounts.utils import get_users_name
from localcontexts.utils import get_site_url

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
import requests
import json

from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenGenerator(PasswordResetTokenGenerator):
    pass

generate_token=TokenGenerator()

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

def send_tagged_mailgun_template_email(email, subject, template_name, data, tag):
    return requests.post(
        settings.MAILGUN_BASE_URL,
        auth=("api", settings.MAILGUN_API_KEY),
        data={
            "from": "Local Contexts Hub <no-reply@localcontextshub.org>",
            "to": email,
            "subject": subject,
            "template": template_name,
            "t:variables": json.dumps(data),
            "o:tag": [tag]
            })

"""
    INTERNAL EMAILS
"""

# Send simple email no attachments
def send_simple_email(email, subject, template):
    return requests.post(
        settings.MAILGUN_BASE_URL,
        auth=("api", settings.MAILGUN_API_KEY),
        data={"from": "Local Contexts Hub <no-reply@localcontextshub.org>",
            "to": [email],
            "subject": subject,
            "html": template}
    )

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

# Send email to any Mailing List (test, researchers, newsletter)
def send_mailing_list_email(mailing_list, subject, template, tag=None):
    response = requests.get(
        ("https://api.mailgun.net/v3/lists/{}@localcontextshub.org/members".format(mailing_list)),
        auth=('api', settings.MAILGUN_API_KEY),
        )
    email = "{}@localcontextshub.org".format(mailing_list)
    data=None
    if tag == None:
        send_mailgun_template_email(email, subject, template, data)
    else:
        send_tagged_mailgun_template_email(email, subject, template, data, tag)

'''
    Add members to newsletter mailing list (updates users already on the mailing list)
'''
def add_to_newsletter_mailing_list(email, name, variables):
    return requests.post(
		"https://api.mailgun.net/v3/lists/newsletter@localcontextshub.org/members",
		auth=("api", settings.MAILGUN_API_KEY),
		data={"subscribed": True,
            "upsert": True,
			"address": email,
			"name": name,
            "vars": variables}
    )

'''
    ADD TO OR UPDATE ACTIVE HUB USER IN MAILING LIST IN PROD ONLY
'''
def add_to_active_users_mailing_list(request, email, name):
    environment = dev_prod_or_local(request.get_host())
    if environment == "PROD":
        return requests.post(
            "https://api.mailgun.net/v3/lists/hub_users@localcontextshub.org/members",
            auth=("api", settings.MAILGUN_API_KEY),
            data={"subscribed": True,
                "upsert": True,
                "address": email,
                "name": name,
            }
        )
    
'''
    REMOVE ACTIVE HUB USER FROM MAILING LIST IN PROD ONLY
'''
def remove_from_active_users_mailing_list(request, email, name):
    environment = dev_prod_or_local(request.get_host())
    if environment == "PROD":
        return requests.post(
            "https://api.mailgun.net/v3/lists/hub_users@localcontextshub.org/members",
            auth=("api", settings.MAILGUN_API_KEY),
            data={"subscribed": False,
                "upsert": True,
                "address": email,
                "name": name,
            }
        )


# Get member info from newsletter mailing list
def get_newsletter_member_info(email):
    return requests.get(
        ("https://api.mailgun.net/v3/lists/newsletter@localcontextshub.org/members"
         "/%s"%email),
        auth=('api', settings.MAILGUN_API_KEY),
        )

# Unsubscribe members from newsletter mailing list (unsubscribe from all topics)
def unsubscribe_from_mailing_list(email, name):
    return requests.post(
		"https://api.mailgun.net/v3/lists/newsletter@localcontextshub.org/members",
		auth=("api", settings.MAILGUN_API_KEY),
		data={"subscribed": False,
            "upsert": True,
			"address": email,
            "name": name}
    )

'''
    RESEARCHERS LIST
'''

def manage_researcher_mailing_list(email, subscribed):
    # subscribed will be a boolean
    return requests.post(
		"https://api.mailgun.net/v3/lists/researchers@localcontextshub.org/members",
		auth = ("api", settings.MAILGUN_API_KEY),
		data = {"subscribed": subscribed, "upsert": True, "address": email,}
    )
        
# Send all Institution and community applications to support or the site admin
def send_hub_admins_application_email(request, organization, data):
    template = ''
    subject = ''

    if isinstance(organization, Community):
        subject = f'New Community Application: {data.community_name}'
        template = render_to_string('snippets/emails/internal/community-application.html', { 'data' : data })
    else: 
        if data.is_ror:
            subject = f'New Institution Application: {data.institution_name}'
        else:
            subject = f'New Institution Application (non-ROR): {data.institution_name}'

        template = render_to_string('snippets/emails/internal/institution-application.html', { 'data' : data })

    # if admin group exists:
    if dev_prod_or_local(request.get_host()) == 'PROD':
        email = 'support@localcontexts.org'
        
        # If file, send as attachment
        if data.support_document:
            send_email_with_attachment(data.support_document, email, subject, template)
        else:
            send_simple_email(email, subject, template)
    else:
        # Send to site admin only (will be typically for testing)
        if data.support_document:
            send_email_with_attachment(data.support_document, settings.SITE_ADMIN_EMAIL, subject, template)
        else:
            send_simple_email(settings.SITE_ADMIN_EMAIL, subject, template)

# Send email to support when a Researcher connects to the Hub in PRODUCTION
def send_email_to_support(researcher):
    template = render_to_string('snippets/emails/internal/researcher-account-connection.html', { 'researcher': researcher })
    name = get_users_name(researcher.user)
    title = f'{name} has created a Researcher Account'
    send_simple_email('support@localcontexts.org', title, template)  

def send_researcher_survey(researcher):
    send_mailgun_template_email(researcher.user.email, 'Local Contexts Hub: Researcher survey', 'researcher_survey', None)

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
    
    activation_url = f'{request.scheme}://{domain}/activate/{uid}/{token}'

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

    activation_url = f'{request.scheme}://{domain}/activate/{uid}/{token}'
    
    data = {'user': user, 'activation_url': activation_url}
    subject = 'Activate Your Local Contexts Hub Profile'
    send_mailgun_template_email(to_email, subject, 'activate_profile', data)


# User has activated account and has logged in: Welcome email
def send_welcome_email(request, user):   
    subject = 'Welcome to Local Contexts Hub!'
    url = get_site_url(request, 'login')
    send_mailgun_template_email(user.email, subject, 'welcome', {"login_url": url})

# TEST THIS
# Email to invite user to join the hub
def send_invite_user_email(request, data):
    subject = 'You have been invited to join the Local Contexts Hub'
    name = get_users_name(data.sender)
    url = get_site_url(request, 'register')
    variables = {"register_url": url, "name": name, "message": data.message}
    send_mailgun_template_email(data.email, subject, 'invite_new_user', variables)

# Anywhere JoinRequest instance is created, 
# will email community or institution creator that someone wants to join the organization
def send_join_request_email_admin(request, join_request, organization):
    name = get_users_name(request.user)
    login_url = get_site_url(request, 'login')

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
            'requester_email': request.user.email,
            'login_url': login_url
        }
    send_mailgun_template_email(send_to_email, subject, 'join_request', data)

# REGISTRY Contact organization email
def send_contact_email(to_email, from_name, from_email, message, account):
    subject = f"{from_name} has sent you a message via Local Contexts Hub"
    from_string = f"{from_name} <{from_email}>"

    if isinstance(account, Institution):
        account_name = account.institution_name
    if isinstance(account, Community):
        account_name = account.community_name
    if isinstance(account, Researcher):
        account_name = 'your researcher account'

    data = { "from_name": from_name, "message": message, "account_name": account_name }

    return requests.post(
        settings.MAILGUN_BASE_URL,
        auth=("api", settings.MAILGUN_API_KEY),
        data={
            "from": from_string,
            "to": to_email,
            "subject": subject,
            "template": "registry_contact",
            "t:variables": json.dumps(data)
            })

"""
    MEMBER INVITE EMAILS
"""

def send_member_invite_email(request, data, account):
    name = get_users_name(data.sender)
    login_url = get_site_url(request, 'login')

    if isinstance(account, Institution):
        org_name = account.institution_name
    if isinstance(account, Community):
        org_name = account.community_name
    
    if data.role == 'admin':
        role = 'Administrator'
    elif data.role == 'editor':
        role = 'Editor'
    elif data.role == 'viewer':
        role = 'Viewer'

    variables = {
        'name': name,
        'username': data.sender.username,
        'role': role,
        'message': data.message,
        'org_name': org_name,
        'login_url':login_url
    }
    subject = f'You have been invited to join {org_name}'
    send_mailgun_template_email(data.receiver.email, subject, 'member_invite', variables)


"""
    NOTICE HAS BEEN PLACED ON A PROJECT AND COMMUNITY HAS BEEN NOTIFIED
"""

# A notice has been applied by researcher or institution
def send_email_notice_placed(request, project, community, account):
    # Can pass instance of institution or researcher as account
    login_url = get_site_url(request, 'login')

    if isinstance(account, Institution):
        subject = f'{account.institution_name} has notified you about a Project'
        placed_by = account.institution_name
    if isinstance(account, Researcher):
        placed_by = get_users_name(account.user) + '(Researcher)'
        subject = f'{placed_by} has notified you about a Project'

    data = {
        'project_title': project.title, 
        'project_description': project.description, 
        'placed_by': placed_by,
        'community_name': community.community_name,
        'login_url': login_url
    }
    send_mailgun_template_email(community.community_creator.email, subject, 'notice_placed', data)


"""
    EMAILS FOR COMMUNITY APP
"""

# When Labels have been applied to a Project
def send_email_labels_applied(request, project, community):
    login_url = get_site_url(request, 'login')
    subject = 'A community has applied Labels to your Project'
    data = {
        'community_name': community.community_name,
        'project_title': project.title,
        'login_url': login_url
    }
    send_mailgun_template_email(project.project_creator.email, subject, 'labels_applied', data)


# Label has been approved or not
def send_email_label_approved(request, label, note_id):
    approver_name = get_users_name(label.approved_by)
    login_url = get_site_url(request, 'login')

    if label.is_approved:
        subject = 'Your Label has been approved'
        approved = True
        note = False
        label_note = False
    else:
        subject = 'Your Label has suggested edits'
        approved = False
        note = True
        label_note = LabelNote.objects.get(id=note_id).note

    data = {
        'approver_name': approver_name,
        'label_name': label.name,
        'approved': approved,
        'community_name': label.community.community_name,
        'note': note,
        'label_note': label_note,
        'login_url': login_url
    }
    send_mailgun_template_email(label.created_by.email, subject, 'label_approved', data)

# You are now a member of institution/community email
def send_membership_email(request, account, receiver, role):
    login_url = get_site_url(request, 'login')
    
    if role == 'admin' or role == 'Admin':
        role_str = 'Administrator'
    elif role == 'editor':
        role_str = 'Editor'
    elif role == 'viewer':
        role_str = 'Viewer'
    else:
        role_str = role

    community = False
    institution = False

    if isinstance(account, Community):
        subject = f'You are now a member of {account.community_name}'
        account_name = account.community_name
        community = True
    if isinstance(account, Institution):
        subject = f'You are now a member of {account.institution_name}'
        account_name = account.institution_name
        institution = True

    data = {
        'role_str': role_str,
        'account_name': account_name,
        'login_url': login_url,
        'community': community,
        'institution': institution
    }
    send_mailgun_template_email(receiver.email, subject, 'member_info', data)

def send_contributor_email(request, account, proj_id, is_adding):
    from projects.models import Project
    project = Project.objects.select_related('project_creator').get(unique_id=proj_id)
    creator_account = ''
    account_name = ''

    created_by = project.project_creator_project.all()[0]
    if created_by.institution:
        creator_account = created_by.institution.institution_name
    elif created_by.community:
        creator_account = created_by.community.community_name
    elif created_by.researcher:
        creator_account = 'Researcher'

    register_url = get_site_url(request, 'register')
    project_creator = get_users_name(project.project_creator)
    login_url = get_site_url(request, 'login')

    if is_adding:        
        if isinstance(account, Community):
            to_email = account.community_creator.email
            subject = "Your community has been added as a contributor on a Project"
            account_name = account.community_name
        if isinstance(account, Institution):
            to_email = account.institution_creator.email
            subject = "Your institution has been added as a contributor on a Project"
            account_name = account.institution_name
        if isinstance(account, Researcher):
            to_email = account.user.email
            subject = "Your researcher account has been added as a contributor on a Project"
            account_name = get_users_name(account.user)

    else:
        subject = "Changes have been made to a Project you're contributing to"
        
        if isinstance(account, Community):
            to_email = account.community_creator.email
        if isinstance(account, Institution):
            to_email = account.institution_creator.email
        if isinstance(account, Researcher):
            to_email = account.user.email

    data = {
        'is_adding': is_adding,
        'project_url': project.project_page,
        'register_url': register_url,
        'login_url': login_url,
        'project_creator': project_creator, 
        'project_title': project.title,
        'account_name': account_name,
        'creator_account': creator_account
    }
    send_mailgun_template_email(to_email, subject, 'contributor', data)
    

def send_project_person_email(request, to_email, proj_id, account):
    from projects.models import Project
    registered = User.objects.filter(email=to_email).exists()
    project = Project.objects.select_related('project_creator').get(unique_id=proj_id)

    project_creator = get_users_name(project.project_creator)
    register_url = get_site_url(request, 'register')
    subject = 'You have been added as a contributor on a Local Contexts Hub Project'

    if isinstance(account, Community):
        account_name = account.community_name
    if isinstance(account, Institution):
        account_name = account.institution_name
    if isinstance(account, Researcher):
        account_name = 'Researcher'

    if '/create-project/' in request.path:

        data = {
            'project_person': True,
            'registered': registered,
            'project_url': project.project_page,
            'register_url': register_url,
            'project_creator': project_creator, 
            'project_title': project.title,
            'account_name': account_name
        }
        send_mailgun_template_email(to_email, subject, 'contributor_project_person', data)

"""
    ADD MAILGUN TEMPLATE AND MAJOR UPDATES
"""

# def add_template(filename, temp_name, description):
#     template = render_to_string(f'snippets/emails/{filename}.html')
#     return requests.post(
#         settings.MAILGUN_TEMPLATE_URL,
#         auth=("api", settings.MAILGUN_API_KEY),
#         data={'template': template,
#               'name': temp_name,
#               'description': description})

# if list, loop over each email.
# def send_update_email(email):
#     send_mailgun_template_email(email, 'Local Contexts Hub Updates', 'hub_updates', None)