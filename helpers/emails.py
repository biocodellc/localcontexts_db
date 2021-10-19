from communities.models import Community
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
import requests
from django.contrib.auth.models import User

from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenGenerator(PasswordResetTokenGenerator):
    pass

generate_token=TokenGenerator()

# Send simple email no attachments
def send_simple_email(to_email, subject, template):
    # Example: send_simple_email('someone@domain.com', 'Hello', 'This is a test email')
    return requests.post(
		settings.MAILGUN_BASE_URL,
		auth=("api", settings.MAILGUN_API_KEY),
		data={"from": "Local Contexts Hub <no-reply@localcontextshub.org>",
			"to": [to_email],
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

# Send all Institution and community applications to the hub_admins group or the site admin
def send_hub_admins_application_email(organization, data, subject):
    template = ''
    is_community = isinstance(organization, Community)
    if is_community:
        template = render_to_string('snippets/emails/community-application.html', { 'data' : data })
    else: 
        template = render_to_string('snippets/emails/institution-application.html', { 'data' : data })

    emails = [settings.SITE_ADMIN_EMAIL, 'support@localcontexts.org']

    # if admin group exists:
    if User.objects.filter(groups__name='hub_admins').exists():
        admin_group = User.objects.filter(groups__name='hub_admins')
        for admin in admin_group:
            emails.append(admin.email)
        
        # If file, send as attachment
        if data.support_document:
            send_email_with_attachment(data.support_document, emails, subject, template)
        else:
            send_simple_email(emails, subject, template)
    else:
        # Send to site admin and support only
        if data.support_document:
            send_email_with_attachment(data.support_document, emails, subject, template)
        else:
            send_simple_email(emails, subject, template)

"""
    EMAILS FOR ACCOUNTS APP
"""

# Registration: User Activation email
def send_activation_email(request, user):
    # Remember the current location
    current_site=get_current_site(request)
    template = render_to_string('snippets/emails/activate.html', 
    {
        'user': user,
        'domain':current_site.domain,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })
    send_simple_email(user.email, 'Activate Your Local Contexts Hub Profile', template)

#  Resend Activation Email
def resend_activation_email(request, active_users):
    to_email= active_users[0].email
    current_site = get_current_site(request)
    message = render_to_string('snippets/emails/activate.html', {
        'user': active_users[0],
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(active_users[0].pk)),
        'token': generate_token.make_token(active_users[0]),
    })
    send_simple_email(to_email, 'Activate Your Local Contexts Hub Profile', message)

# User has activated account and has logged in: Welcome email
def send_welcome_email(user):   
    subject = 'Welcome to Local Contexts Hub!'
    template = render_to_string('snippets/emails/welcome.html')
    send_simple_email(user.email, subject, template)

# Email to invite user to join the hub
def send_invite_user_email(request, data):
    current_site=get_current_site(request)
    template = render_to_string('snippets/emails/invite-new-user.html', { 
        'data': data, 
        'domain': current_site.domain, 
    })
    send_simple_email(data.email, 'You have been invited to join the Local Contexts Hub', template)

# Anywhere JoinRequest instance is created, 
# will email community or institution creator that someone wants to join the organization
def send_join_request_email_admin(user, organization):
    template = render_to_string('snippets/emails/join-request.html', {
        'user': user,
        'organization': organization,
    })
    # Check if organization instance is community model
    is_community = isinstance(organization, Community)
    if is_community:
        send_simple_email(organization.community_creator.email, 'Someone has requested to join your community', template)
    else:
        send_simple_email(organization.institution_creator.email, 'Someone has requested to join your institution', template)

"""
    EMAILS FOR INSTITUTION APP
"""

def send_institution_invite_email(data, institution):
    template = render_to_string('snippets/emails/member-invite.html', { 
        'data': data,
        'institution': institution 
    })
    send_simple_email(data.receiver.email, 'You have been invited to join an institution', template)
    

"""
    EMAILS FOR COMMUNITY APP
"""

# Inviting a user to join community
def send_community_invite_email(data, community):
    template = render_to_string('snippets/emails/member-invite.html', { 
        'data': data,
        'community': community 
    })
    send_simple_email(data.receiver.email, 'You have been invited to join a community', template)

# When Labels have been applied to a Project
def send_email_labels_applied(project, community):
    template = render_to_string('snippets/emails/labels-applied.html', {
        'project': project,
        'community': community,
    })
    send_simple_email(project.project_creator.email, 'A community has applied Labels to your Project', template)