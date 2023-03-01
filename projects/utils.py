from researchers.models import Researcher
from institutions.models import Institution
from communities.models import Community
from projects.models import ProjectContributors, ProjectActivity
from helpers.emails import send_contributor_email
from notifications.utils import send_simple_action_notification
from helpers.models import ProjectStatus
from django.core.paginator import Paginator
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from accounts.utils import get_users_name

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

# TODO: FIX THIS
def add_to_contributors(request, account, project):
    contributors = ProjectContributors.objects.get(project=project)
    
    incoming_institutions_list = request.POST.getlist('selected_institutions')
    incoming_researchers_list = request.POST.getlist('selected_researchers')
    incoming_communities_list = request.POST.getlist('selected_communities')
    print(f'FIRST: {incoming_communities_list}, {incoming_institutions_list}, {incoming_researchers_list}')

    # FIXME: on edit, removes all other contributors besides the ones added. check contents of incoming lists and ids_to_remove
    if '/edit-project/' in request.path:
        # on edit projects: two things need to happen: 
        # 1. added accounts need to be added & existing ones removed 
        # 2. accounts that were not removed need to be informed of edits

        # if isinstance(account, Community):
        #     incoming_communities_list.remove(account.id)
        # if isinstance(account, Researcher):
        #     incoming_researchers_list.remove(account.id)
        # if isinstance(account, Institution):
        #     incoming_institutions_list.remove(account.id)
        print(account, account.id)

        print(f'SECOND: {incoming_communities_list}, {incoming_institutions_list}, {incoming_researchers_list}')

        if incoming_institutions_list:
            current_ids = list(contributors.institutions.all().values_list('id', flat=True)) # current list of institutions
            matching_ids = list(set(current_ids) & set(incoming_institutions_list)) # getting matching ids from the current list and the incoming list
            unmatching_incoming_ids = [i for i in incoming_institutions_list if i not in current_ids] # getting unmatching ids from incoming list
            ids_to_remove = [i for i in current_ids if i not in incoming_institutions_list] # getting ids that are in current ids but not in incoming ids
            
            if matching_ids:
                for institution in Institution.objects.filter(id__in=matching_ids):
                    send_simple_action_notification(None, institution, 'Edits have been made to a Project', 'Projects', project.unique_id)
                    # send_contributor_email(request, institution, project.unique_id, False)
            
            if unmatching_incoming_ids:
                contributors.institutions.set(unmatching_incoming_ids)
                for institution in Institution.objects.filter(id__in=unmatching_incoming_ids):
                    send_simple_action_notification(None, institution, 'Your institution has been added as a contributor on a Project', 'Projects', project.unique_id)
                    # send_contributor_email(request, institution, project.unique_id, True)
            
            if ids_to_remove:
                for id in ids_to_remove:
                    contributors.institutions.remove(id)
    
        if incoming_researchers_list:
            current_ids = list(contributors.researchers.all().values_list('id', flat=True)) # current list of researchers
            matching_ids = list(set(current_ids) & set(incoming_researchers_list)) # getting matching ids from the current list and the incoming list
            unmatching_incoming_ids = [i for i in incoming_researchers_list if i not in current_ids] # getting unmatching ids from incoming list
            ids_to_remove = [i for i in current_ids if i not in incoming_researchers_list] # getting ids that are in current ids but not in incoming ids
            
            if matching_ids:
                for researcher in Researcher.objects.filter(id__in=matching_ids):
                    send_simple_action_notification(None, researcher, 'Edits have been made to a Project', 'Projects', project.unique_id)
                    # send_contributor_email(request, researcher, project.unique_id, False)
            
            if unmatching_incoming_ids:
                contributors.researchers.set(unmatching_incoming_ids)
                for researcher in Researcher.objects.filter(id__in=unmatching_incoming_ids):
                    send_simple_action_notification(None, researcher, 'You have been added as a contributor on a Project', 'Projects', project.unique_id)
                    # send_contributor_email(request, researcher, project.unique_id, True)
            
            if ids_to_remove:
                for id in ids_to_remove:
                    contributors.researchers.remove(id)
        
            if incoming_communities_list:
                current_ids = list(contributors.communities.all().values_list('id', flat=True)) # current list of communities
                matching_ids = list(set(current_ids) & set(incoming_communities_list)) # getting matching ids from the current list and the incoming list
                unmatching_incoming_ids = [i for i in incoming_communities_list if i not in current_ids] # getting unmatching ids from incoming list
                ids_to_remove = [i for i in current_ids if i not in incoming_communities_list] # getting ids that are in current ids but not in incoming ids
                
                if matching_ids:
                    for community in Community.objects.filter(id__in=matching_ids):
                        send_simple_action_notification(None, community, 'Edits have been made to a Project', 'Projects', project.unique_id)
                        # send_contributor_email(request, community, project.unique_id, False)
                
                if unmatching_incoming_ids:
                    contributors.communities.set(unmatching_incoming_ids)
                    for community in Community.objects.filter(id__in=unmatching_incoming_ids):
                        send_simple_action_notification(None, community, 'Your community has been as a contributor on a Project', 'Projects', project.unique_id)
                        # send_contributor_email(request, community, project.unique_id, True)
                
                if ids_to_remove:
                    for id in ids_to_remove:
                        contributors.communities.remove(id)
        
    elif '/create-project/' in request.path:
        # add creator as a contributor
        if isinstance(account, Community):
            contributors.communities.add(account)
        if isinstance(account, Researcher):
            contributors.researchers.add(account)
        if isinstance(account, Institution):
            contributors.institutions.add(account)

        contributors.institutions.set(incoming_institutions_list) # add selected contribs to contribs
        selected = Institution.objects.filter(id__in=incoming_institutions_list)
        for institution in selected:
            send_simple_action_notification(None, institution, 'Your institution has been added as a contributor on a Project', 'Projects', project.unique_id)
            send_contributor_email(request, institution, project.unique_id, True)

        contributors.researchers.set(incoming_researchers_list) # add selected contribs to contribs
        selected = Researcher.objects.filter(id__in=incoming_researchers_list)
        for researcher in selected:
            send_simple_action_notification(None, researcher, 'You have been added as a contributor on a Project', 'Projects', project.unique_id)
            send_contributor_email(request, researcher, project.unique_id, True)

        contributors.communities.set(incoming_communities_list) # add selected contribs to contribs
        selected = Community.objects.filter(id__in=incoming_communities_list)
        for community in selected:
            send_simple_action_notification(None, community, 'Your community has been as a contributor on a Project', 'Projects', project.unique_id)
            send_contributor_email(request, community, project.unique_id, True)





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