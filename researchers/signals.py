from django.db.models.signals import pre_delete
from django.dispatch import receiver
from researchers.models import Researcher
from django.contrib.auth.models import User
from helpers.emails import manage_researcher_mailing_list

def remove_email_on_delete(email):
    if email:
        manage_researcher_mailing_list(email, False)

@receiver(pre_delete, sender=User)
def remove_from_mailing_list_on_delete_user(sender, instance, *args, **kwargs):
    if Researcher.objects.filter(user=instance).exists():
        email = Researcher.objects.get(user=instance).contact_email or instance.email
        remove_email_on_delete(email)

@receiver(pre_delete, sender=Researcher)
def remove_from_mailing_list_on_delete_researcher(sender, instance, *args, **kwargs):
    email = instance.contact_email or instance.user.email
    remove_email_on_delete(email)
