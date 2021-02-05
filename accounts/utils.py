from django.contrib.auth.models import User
from researchers.models import Researcher
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenGenerator(PasswordResetTokenGenerator):
    pass

generate_token=TokenGenerator()

def email_exists(email):
    if User.objects.filter(email=email).exists():
        return True
    else:
        return False

def is_user_researcher(user):
    target_user = Researcher.objects.filter(user=user).exists()
    if target_user:
        return Researcher.objects.get(user=user)
    else:
        return False
