from researchers.models import Researcher
from institutions.models import Institution
from communities.models import Community
from projects.models import ProjectActivity, ProjectContributors
from helpers.emails import send_contributor_email
from notifications.utils import send_simple_action_notification
from helpers.models import ProjectStatus
from django.core.paginator import Paginator
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from accounts.utils import get_users_name
import itertools
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from localcontexts.utils import dev_prod_or_local

# PROJECT STATUS 
def set_project_status(user, project, community, creator, project_status):
    truncated_project_title = str(project.title)[0:30]
    reference_id = project.unique_id
    name = get_users_name(user)

    statuses = ProjectStatus.objects.filter(project=project, community=community)

    title = ''
    for status in statuses:
        status.seen = True

        if project_status == 'seen':
            title = f'{community.community_name} has seen and acknowledged your Project: {truncated_project_title}'
            ProjectActivity.objects.create(project=project, activity=f'{name} from {community.community_name} set the Project status to Seen')

        if project_status == 'pending':
            status.status = 'pending'
            title = f'{community.community_name} is in the process of applying Labels to your Project: {truncated_project_title}'
            ProjectActivity.objects.create(project=project, activity=f'{name} from {community.community_name} set the Project status to Labels Pending')

        if project_status == 'not_pending':
            status.status = 'not_pending'
            title = f'{community.community_name} will not be applying Labels to your Project: {truncated_project_title}'
            ProjectActivity.objects.create(project=project, activity=f'{name} from {community.community_name} set the Project status to No Labels Pending')

        status.save()

        # Send Notification
        if creator.institution:
            send_simple_action_notification(user, creator.institution, title, 'Projects', reference_id)
        if creator.researcher:
            send_simple_action_notification(user, creator.researcher, title, 'Projects', reference_id)

def project_status_seen_at_comment(user, community, creator, project):
    if ProjectStatus.objects.filter(project=project, community=community).exists():
        status = ProjectStatus.objects.get(project=project, community=community)

        truncated_project_title = str(project.title)[0:30]
        reference_id = project.unique_id

        # If message is sent, set notice status to 'Seen'
        if status.seen == False:
            status.seen = True
            status.save()

            title = f'{community.community_name} has added a comment to your Project: {truncated_project_title}'

            # Send Notification
            if creator.institution:
                send_simple_action_notification(user, creator.institution, title, 'Projects', reference_id)
            if creator.researcher:
                send_simple_action_notification(user, creator.researcher, title, 'Projects', reference_id)

# CONTRIBUTORS
def process_contributors(request, project, contributors, current_ids, incoming_ids, model):
    matching_ids = list(set(current_ids) & set(incoming_ids))
    unmatching_ids = [i for i in incoming_ids if i not in current_ids]
    ids_to_remove = [i for i in current_ids if i not in incoming_ids]

    for item in model.objects.filter(id__in=matching_ids):
        send_simple_action_notification(None, item, 'Edits have been made to a Project', 'Projects', project.unique_id)
        send_contributor_email(request, item, project.unique_id, False)

    for item in model.objects.filter(id__in=unmatching_ids):
        contributors.add(item)

        if isinstance(item, Institution):
            account = 'institution account'
        elif isinstance(item, Researcher):
            account = 'researcher account'
        elif isinstance(item, Community):
            account = 'community account'

        send_simple_action_notification(None, item, f'Your {account} has been added as a contributor on a Project', 'Projects', project.unique_id)
        send_contributor_email(request, item, project.unique_id, True)

    for id in ids_to_remove:
        contributors.remove(id)

def add_to_contributors(request, account, project):
    contributors = ProjectContributors.objects.get(project=project)
    # Ensure all lists are int
    institutions_list = [eval(i) for i in request.POST.getlist('selected_institutions')]
    researchers_list = [eval(i) for i in request.POST.getlist('selected_researchers')]
    communities_list = [eval(i) for i in request.POST.getlist('selected_communities')]

    if project.project_privacy == 'Private':
        if any([institutions_list, researchers_list, communities_list]):
            project.project_privacy = 'Contributor'
            project.save()

    if '/edit-project/' in request.path:
        current_institution_ids = list(contributors.institutions.all().values_list('id', flat=True)) # current list of institutions
        current_researcher_ids = list(contributors.researchers.all().values_list('id', flat=True)) # current list of researchers
        current_community_ids = list(contributors.communities.all().values_list('id', flat=True)) # current list of communities

        if isinstance(account, Institution):
            if account.id in current_institution_ids:
                current_institution_ids.remove(account.id) # Project creator account is removed from list of possible institutions
            if account.id in institutions_list:
                institutions_list.remove(account.id)
        elif isinstance(account, Researcher):
            if account.id in current_researcher_ids:
                current_researcher_ids.remove(account.id) # Project creator account is removed from list of possible researchers
            if account.id in researchers_list:
                researchers_list.remove(account.id)
        elif isinstance(account, Community):
            if account.id in current_community_ids:
                current_community_ids.remove(account.id) # Project creator account is removed from list of possible communities
            if account.id in communities_list:
                communities_list.remove(account.id)
        
        process_contributors(request, project, contributors.institutions, current_institution_ids, institutions_list, Institution)
        process_contributors(request, project, contributors.researchers, current_researcher_ids, researchers_list, Researcher)
        process_contributors(request, project, contributors.communities, current_community_ids, communities_list, Community)
        
    elif '/create-project/' in request.path:
        # add creator as a contributor
        if isinstance(account, Community):
            contributors.communities.add(account)
        if isinstance(account, Researcher):
            contributors.researchers.add(account)
        if isinstance(account, Institution):
            contributors.institutions.add(account)

        for institution in Institution.objects.filter(id__in=institutions_list):
            contributors.institutions.add(institution) # add selected contribs to contribs
            send_simple_action_notification(None, institution, 'Your institution has been added as a contributor on a Project', 'Projects', project.unique_id)
            send_contributor_email(request, institution, project.unique_id, True)

        for researcher in Researcher.objects.filter(id__in=researchers_list):
            contributors.researchers.add(researcher) # add selected contribs to contribs
            send_simple_action_notification(None, researcher, 'You have been added as a contributor on a Project', 'Projects', project.unique_id)
            send_contributor_email(request, researcher, project.unique_id, True)

        for community in Community.objects.filter(id__in=communities_list):
            contributors.communities.add(community) # add selected contribs to contribs
            send_simple_action_notification(None, community, 'Your community has been as a contributor on a Project', 'Projects', project.unique_id)
            send_contributor_email(request, community, project.unique_id, True)


# PAGINATION FOR PROJECTS
def paginate(request, queryset, num_of_pages):
    p = Paginator(queryset, num_of_pages)
    page_num = request.GET.get('page', 1)
    page = p.page(page_num)
    return page

def return_project_search_results(request, queryset):
    q = request.GET.get('q')
    if q:
        vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
        query = SearchQuery(q)
        results = queryset.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
    else:
        results = None
    return results

def return_project_labels_by_community(project):
    bc_labels = BCLabel.objects.filter(project_bclabels=project).select_related('community').order_by('community__community_name', 'name')
    tk_labels = TKLabel.objects.filter(project_tklabels=project).select_related('community').order_by('community__community_name', 'name')
    
    label_groups = {}
    for community, group in itertools.groupby(bc_labels, key=lambda x: x.community):
        bc_labels_list = list(group)
        label_groups.setdefault(community, {'bc_labels': bc_labels_list, 'tk_labels': [], 'bc_label_count': len(bc_labels_list), 'tk_label_count': 0})
        
    for community, group in itertools.groupby(tk_labels, key=lambda x: x.community):
        tk_labels_list = list(group)
        if community in label_groups:
            label_groups[community]['tk_labels'] = tk_labels_list
            label_groups[community]['tk_label_count'] = len(tk_labels_list)
        else:
            label_groups[community] = {'bc_labels': [], 'tk_labels': tk_labels_list, 'bc_label_count': 0, 'tk_label_count': len(tk_labels_list)}
        
    return label_groups

def can_download_project(request, project_creator_instance):
    can_download = True
    if dev_prod_or_local(request.get_host()) == 'DEV':
        can_download = False
    elif project_creator_instance.community:
        if not project_creator_instance.community.is_approved:
            can_download = False
    elif project_creator_instance.institution:
        if not project_creator_instance.institution.is_approved:
            can_download = False
    return can_download
