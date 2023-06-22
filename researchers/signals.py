from django.db.models.signals import post_delete
from django.dispatch import receiver
from researchers.models import Researcher
from django.contrib.auth.models import User
from helpers.emails import manage_researcher_mailing_list

@receiver(post_delete, sender=User)
def delete_action_notifications(sender, instance, *args, **kwargs):
    if Researcher.objects.filter(user=instance).exists():
        researcher = Researcher.objects.get(user=instance)
        if researcher.contact_email:
            manage_researcher_mailing_list(researcher.contact_email, False)
        else:
            manage_researcher_mailing_list(instance.email, False)

@receiver(post_delete, sender=Researcher)
def delete_action_notifications(sender, instance, *args, **kwargs):
    if instance.contact_email:
        manage_researcher_mailing_list(instance.contact_email, False)
    else:
        manage_researcher_mailing_list(instance.user.email, False)
