from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
import requests
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
