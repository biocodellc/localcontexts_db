import json

from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from .models import Connections, Notice, InstitutionNotice

def set_notice_defaults(notice):
    if isinstance(notice, Notice):
        bc_text = 'The BC (Biocultural) Notice is a visible notification that there are accompanying cultural rights and responsibilities that need further attention for any future sharing and use of this material or data. The BC Notice recognizes the rights of Indigenous peoples to permission the use of information, collections, data and digital sequence information (DSI) generated from the biodiversity or genetic resources associated with traditional lands, waters, and territories. The BC Notice may indicate that BC Labels are in development and their implementation is being negotiated.'
        tk_text = 'The TK (Traditional Knowledge) Notice is a visible notification that there are accompanying cultural rights and responsibilities that need further attention for any future sharing and use of this material. The TK Notice may indicate that TK Labels are in development and their implementation is being negotiated.'
        bc_url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/bc-notice.png'
        tk_url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/tk-notice.png'
        
        if notice.notice_type == 'biocultural':
            notice.bc_img_url = bc_url
            notice.bc_default_text = bc_text
        if notice.notice_type == 'traditional_knowledge':
            notice.tk_img_url = tk_url
            notice.tk_default_text = tk_text
        if notice.notice_type == 'biocultural_and_traditional_knowledge':
            notice.bc_img_url = bc_url
            notice.bc_default_text = bc_text
            notice.tk_img_url = tk_url
            notice.tk_default_text = tk_text
    elif isinstance(notice, InstitutionNotice):
        attribution_incomplete_text = 'Collections and items in our institution have incomplete, inaccurate, and/or missing attribution. We are using this notice to clearly identify this material so that it can be updated, or corrected by communities of origin. Our institution is committed to collaboration and partnerships to address this problem of incorrect or missing attribution.'
        open_to_collaborate_text = 'Our institution is committed to the development of new modes of collaboration, engagement, and partnership with Indigenous peoples for the care and stewardship of past and future heritage collections.'
        attribution_incomplete_url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/ci-notice-attribution-incomplete.png'
        open_to_collaborate_url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/ci-notice-open-to-collaborate.png'
        
        if notice.notice_type == 'open_to_collaborate':
            notice.open_to_collaborate_img_url = open_to_collaborate_url
            notice.open_to_collaborate_default_text = open_to_collaborate_text
        if notice.notice_type == 'attribution_incomplete':
            notice.attribution_incomplete_img_url = attribution_incomplete_url
            notice.attribution_incomplete_default_text = attribution_incomplete_text
        if notice.notice_type == 'open_to_collaborate_and_attribution_incomplete':
            notice.open_to_collaborate_img_url = open_to_collaborate_url
            notice.open_to_collaborate_default_text = open_to_collaborate_text
            notice.attribution_incomplete_img_url = attribution_incomplete_url
            notice.attribution_incomplete_default_text = attribution_incomplete_text

    notice.save()  

def dev_prod_or_local(hostname):
    if 'anth-ja77-lc-dev-42d5' in hostname:
        return 'DEV'
    elif 'localcontextshub' in hostname:
        return 'PROD'
    elif 'anth-ja77-local-contexts-8985' in hostname:
        return 'AE_PROD' 

def get_labels_json():
    json_data = open('./localcontexts/static/json/Labels.json')
    data = json.load(json_data) #deserialize
    return data

def add_to_connections(target_org, org):
    connections = ''

    if isinstance(target_org, Community):
        connections = Connections.objects.get(community=target_org)
        if isinstance(org, Institution):
            connections.institutions.add(org)
        if isinstance(org, Researcher):
            connections.researchers.add(org)

    if isinstance(target_org, Institution):
        connections = Connections.objects.get(institution=target_org)
        if isinstance(org, Community):
            connections.communities.add(org)

    if isinstance(target_org, Researcher):
        connections = Connections.objects.get(researcher=target_org)
        if isinstance(org, Community):
            connections.communities.add(org)
                
    connections.save()

def loop_through_notices(list, institution, project):
    for selected in list:
        if selected == 'bcnotice':
            notice = Notice.objects.create(notice_type='biocultural', placed_by_institution=institution, project=project)
        elif selected == 'tknotice':
            notice = Notice.objects.create(notice_type='traditional_knowledge', placed_by_institution=institution, project=project)
        elif selected == 'open_to_collaborate':
            notice = InstitutionNotice.objects.create(notice_type='open_to_collaborate', institution=institution, project=project)
        elif selected == 'attribution_incomplete':
            notice = InstitutionNotice.objects.create(notice_type='attribution_incomplete', institution=institution, project=project)
        
        set_notice_defaults(notice)


# Create Notices (institutions)
def create_notices(selected_notices, institution, project):
    # selected_notices would be a list: 
    # attribution_incomplete # open_to_collaborate # bcnotice # tknotice

    # If Individual notices
    if len(selected_notices) == 1:
        loop_through_notices(selected_notices, institution, project)

    elif len(selected_notices) == 2:
        # If BC and TK Notices
        if 'bcnotice' in selected_notices and 'tknotice' in selected_notices:
            notice = Notice.objects.create(notice_type='biocultural_and_traditional_knowledge', placed_by_institution=institution, project=project)
            set_notice_defaults(notice)

        # If both institution notices
        elif 'open_to_collaborate' in selected_notices and 'attribution_incomplete' in selected_notices:
            institution_notice = InstitutionNotice.objects.create(notice_type='open_to_collaborate_and_attribution_incomplete', institution=institution, project=project)
            set_notice_defaults(institution_notice)
        else:
            loop_through_notices(selected_notices, institution, project)

    elif len(selected_notices) == 3:
        # Both BC and TK and one of the institution notices
        if 'bcnotice' in selected_notices and 'tknotice' in selected_notices:
            notice = Notice.objects.create(notice_type='biocultural_and_traditional_knowledge', placed_by_institution=institution, project=project)
            set_notice_defaults(notice)
            if 'open_to_collaborate' in selected_notices:
                institution_notice = InstitutionNotice.objects.create(notice_type='open_to_collaborate', institution=institution, project=project)
                set_notice_defaults(institution_notice)
            else:
                institution_notice = InstitutionNotice.objects.create(notice_type='attribution_incomplete', institution=institution, project=project)
                set_notice_defaults(institution_notice)

        # Both institution notices and one of either tk or bc
        elif 'open_to_collaborate' in selected_notices and 'attribution_incomplete' in selected_notices:
            institution_notice = InstitutionNotice.objects.create(notice_type='open_to_collaborate_and_attribution_incomplete', institution=institution, project=project)
            set_notice_defaults(institution_notice)
            if 'bcnotice' in selected_notices:
                notice = Notice.objects.create(notice_type='biocultural', placed_by_institution=institution, project=project)
                set_notice_defaults(notice)
            else:
                notice = Notice.objects.create(notice_type='traditional_knowledge', placed_by_institution=institution, project=project)
                set_notice_defaults(notice)

    # If all four notices
    elif len(selected_notices) == 4:
        notice = Notice.objects.create(notice_type='biocultural_and_traditional_knowledge', placed_by_institution=institution, project=project)
        set_notice_defaults(notice)
        institution_notice = InstitutionNotice.objects.create(notice_type='open_to_collaborate_and_attribution_incomplete', institution=institution, project=project)
        set_notice_defaults(institution_notice)

