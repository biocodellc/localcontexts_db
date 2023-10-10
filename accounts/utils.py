from django.utils.http import url_has_allowed_host_and_scheme

from django.conf import settings
from django.db.models import Q

from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from tklabels.models import TKLabel
from bclabels.models import BCLabel

from unidecode import unidecode

def get_users_name(user):
    if user:
        return user.get_full_name() or user.username
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
    combined_accounts = []

    if community_accounts is not None:
        combined_accounts.extend(community_accounts)

    combined_accounts.extend(researcher_accounts)
    combined_accounts.extend(institution_accounts)

    cards = sorted(combined_accounts, key=lambda obj: (
        unidecode(obj.community_name.lower().strip()) if isinstance(obj, Community) else 
        unidecode(obj.institution_name.lower().strip()) if isinstance(obj, Institution) else
        unidecode(obj.user.first_name.lower().strip()) if isinstance(obj, Researcher) and obj.user.first_name.strip() else
        unidecode(obj.user.username.lower().strip()) if isinstance(obj, Researcher) else ''
    ))

    return cards

def get_next_path(request, user, default_path: str):
    next_path = request.POST.get('next')

    user_institutions = Institution.objects.filter(Q(institution_creator=user) | Q(admins=user) | Q(editors=user)) 
    user_communities = Community.objects.filter(Q(community_creator=user) | Q(admins=user) | Q(editors=user)).first()

    unapproved_label = (
        TKLabel.objects.filter(
            Q(community__community_creator=user) |
            Q(community__admins=user) |
            Q(community__editors=user),
            is_approved=False
        ).prefetch_related('community').first() or
        BCLabel.objects.filter(
            Q(community__community_creator=user) |
            Q(community__admins=user) |
            Q(community__editors=user),
            is_approved=False
        ).prefetch_related('community').first())
    
    institution = user_institutions.filter(institution_created_project__project__project_creator=user).first()

    if user_communities:
        if unapproved_label:
            pk = unapproved_label.community.id
            next_path = 'select-label'
            return [next_path, pk]
        else:
            pk = user_communities.id
            next_path = 'community-projects'
            return [next_path, pk]

    if user_institutions:
        if institution:
            pk = institution.id
            next_path = 'institution-projects'
            return [next_path, pk]
        else:
            pk = user_institutions.first().id
            next_path = 'institution-notices'
            return [next_path, pk]

    # validate next_path exists and is not an open redirect
    if next_path and url_has_allowed_host_and_scheme(next_path, settings.ALLOWED_HOSTS):
        return [next_path]

    return [default_path]
