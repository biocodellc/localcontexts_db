# Imports for sending emails
from django.core import signing
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site

import requests

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

from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenGenerator(PasswordResetTokenGenerator):
    pass

generate_token=TokenGenerator()

def email_exists(email):
    email_exists = User.objects.filter(email=email).exists()
    return email_exists

def send_activation_email(request, user, to_email):
    # Remember the current location
    current_site=get_current_site(request)
    template = render_to_string('snippets/activate.html', 
    {
        'user': user,
        'domain':current_site.domain,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })
    send_simple_email(to_email, 'Activate Your Local Contexts Hub Profile', template)

    # !! Keep until Prod testing works !!
    # email_contents = EmailMessage(
    #     #Email subject
    #     'Activate Your Local Contexts Hub Account',
    #     #Body of the email
    #     template,
    #     #Sender
    #     settings.EMAIL_HOST_USER,
    #     #Recipient, in list to send to multiple addresses at a time.
    #     [to_email]
    # )
    # email_contents.fail_silently=False
    # email_contents.send()


def resend_activation_email(request, active_users):
    to_email= active_users[0].email
    current_site = get_current_site(request)
    email_subject = 'Activate Your Account'
    message = render_to_string('snippets/activate.html', {
        'user': active_users[0],
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(active_users[0].pk)),
        'token': generate_token.make_token(active_users[0]),
    })
    
    # !! Keep until Prod testing works !!
    # active_users[0].email_user(email_subject, message)

    send_simple_email(to_email, 'Activate Your Local Contexts Hub Profile', message)