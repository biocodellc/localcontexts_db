from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenGenerator(PasswordResetTokenGenerator):
    pass

generate_token=TokenGenerator()

def email_exists(email):
    if User.objects.filter(email=email).exists():
        return True
    else:
        return False
