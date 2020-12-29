from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import *

@receiver(pre_save, sender=BCLabel)
def add_default_text(sender, instance, *args, **kwargs):
    if instance.label_type == 'provenance':
        instance.default_text = "This Label is being used to affirm an inherent interest Indigenous people have in the scientific collections and data about communities, peoples, and the biodiversity found within traditional lands, waters and territories. [Community name or authorizing party] has permissioned the use of this collection and associated data for research purposes, and retains the right to be named and associated with it into the future. This association reflects a significant relationship and responsibility to [the species or biological entity] and associated scientific collections and data."
    elif instance.label_type == 'commercialization':
        instance.default_text = "This Label is being used to indicate that [community name or authorizing party] is open to commercialization opportunities that might derive from any information, collections, data and DSI to which this Label is connected. As a primary party in any partnership and collaboration opportunities that emerge from the use of these resources, we retain an express interest in any future negotiations."
    elif instance.label_type == 'collaboration':
        instance.default_text = "This Label is being used to make clear [community name or authorizing body] is open to future engagement, collaboration, and partnership around research and outreach opportunities."
    elif instance.label_type == 'consent_verified':
        instance.default_text = "This Label is being used to verify that [community name or authorizing party] have consent conditions in place for the use of this information, collections, data and digital sequence information."
    elif instance.label_type == 'multiple_community':
        instance.default_text = "This Label is being used to affirm responsibility and ownership over this information, collection, data and digital sequence information is spread across several distinct communities. Use will be dependent upon discussion and negotiation with multiple communities."
    elif instance.label_type == 'research':
        instance.default_text = "This Label is being used by [community name or authorizing body] to allow this information, collection, data and digital sequence information to be used for unspecified research purposes. This Label does not provide permission for commercialization activities.  [Optional return of research results statement]."
    
