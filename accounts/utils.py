from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
import itertools
from unidecode import unidecode

def get_users_name(user):
    if user is not None:
        if user.get_full_name():
            return user.get_full_name()
        else:
            return user.username
    else:
        return None

def manage_mailing_list(request, first_name, emailb64):
    selections = request.POST.getlist('topic')
    tech = 'no'
    news = 'no'
    events = 'no'
    notice = 'no'
    labels = 'no'
    for item in selections:
        if item == 'tech':
            tech = 'yes'
        if item == 'news':
            news = 'yes'
        if item == 'events':
            events = 'yes'
        if item == 'notice':
            notice = 'yes'
        if item == 'labels':
            labels = 'yes'
    variables = '{"first_name":"%s", "tech": "%s", "news": "%s", "events": "%s","notice": "%s","labels": "%s", "id": "%s"}'%(first_name, tech, news, events, notice, labels, emailb64)
    return(variables)

def return_registry_accounts(community_accounts, researcher_accounts, institution_accounts):
    # Accounts combined and then sorted Alphabetically (Desc) Lower and strip added to sort alphabetically properly ignoring case and empty strings
    combined_accounts = list(itertools.chain(community_accounts, researcher_accounts, institution_accounts))
    cards = sorted(combined_accounts, key=lambda obj: (
        unidecode(obj.community_name.lower().strip()) if isinstance(obj, Community) else 
        unidecode(obj.institution_name.lower().strip()) if isinstance(obj, Institution) else
        unidecode(obj.user.first_name.lower().strip()) if isinstance(obj, Researcher) and obj.user.first_name.strip() else
        unidecode(obj.user.username.lower().strip()) if isinstance(obj, Researcher) else ''
    ))
    # unidecode allows for the accounts to be sorted based on the alphabet, excluding accents
    return cards