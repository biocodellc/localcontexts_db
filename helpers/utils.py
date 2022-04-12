import json
import requests
import zipfile
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa

from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from .models import Connections, Notice, InstitutionNotice

def change_member_role(org, member, current_role, new_role):
    print(current_role, new_role)
    if current_role == 'admin':
        org.admins.remove(member)
    elif current_role == 'editor':
        org.editors.remove(member)
    else:
        org.viewers.remove(member)
    
    if new_role == 'Administrator':
        org.admins.add(member)
    elif new_role == 'Editor':
        org.editors.add(member)
    else:
        org.viewers.add(member)

def set_language_code(instance):
    url = 'https://raw.githubusercontent.com/biocodellc/localcontexts_json/main/data/ianaObj.json'
    data = requests.get(url).json()

    if instance.language in data.keys():
        instance.language_tag = data[instance.language]
        instance.save()


# h/t: https://stackoverflow.com/questions/59695870/generate-multiple-pdfs-and-zip-them-for-download-all-in-a-single-view
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    buffer = BytesIO()
    p = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), buffer)
    pdf = buffer.getvalue()
    buffer.close()
    if not p.err:
        return pdf
    return None

def generate_zip(files):
    mem_zip = BytesIO()

    with zipfile.ZipFile(mem_zip, mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.writestr(f[0], f[1])

    return mem_zip.getvalue()

def set_notice_defaults(notice):
    baseURL = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/'
    if isinstance(notice, Notice):
        bc_text = 'The BC (Biocultural) Notice is a visible notification that there are accompanying cultural rights and responsibilities that need further attention for any future sharing and use of this material or data. The BC Notice recognizes the rights of Indigenous peoples to permission the use of information, collections, data and digital sequence information (DSI) generated from the biodiversity or genetic resources associated with traditional lands, waters, and territories. The BC Notice may indicate that BC Labels are in development and their implementation is being negotiated.'
        tk_text = 'The TK (Traditional Knowledge) Notice is a visible notification that there are accompanying cultural rights and responsibilities that need further attention for any future sharing and use of this material. The TK Notice may indicate that TK Labels are in development and their implementation is being negotiated.'
        
        if notice.notice_type == 'biocultural':
            notice.bc_img_url = baseURL + 'bc-notice.png'
            notice.bc_svg_url = baseURL + 'bc-notice.svg'
            notice.bc_default_text = bc_text
        if notice.notice_type == 'traditional_knowledge':
            notice.tk_img_url = baseURL + 'tk-notice.png'
            notice.tk_svg_url = baseURL + 'tk-notice.svg'
            notice.tk_default_text = tk_text

        if notice.notice_type == 'biocultural_and_traditional_knowledge':
            notice.bc_img_url = baseURL + 'bc-notice.png'
            notice.bc_svg_url = baseURL + 'bc-notice.svg'
            notice.bc_default_text = bc_text
            notice.tk_img_url = baseURL + 'tk-notice.png'
            notice.tk_svg_url = baseURL + 'tk-notice.svg'
            notice.tk_default_text = tk_text
    elif isinstance(notice, InstitutionNotice):
        attribution_incomplete_text = 'Collections and items in our institution have incomplete, inaccurate, and/or missing attribution. We are using this notice to clearly identify this material so that it can be updated, or corrected by communities of origin. Our institution is committed to collaboration and partnerships to address this problem of incorrect or missing attribution.'
        open_to_collaborate_text = 'Our institution is committed to the development of new modes of collaboration, engagement, and partnership with Indigenous peoples for the care and stewardship of past and future heritage collections.'
        
        if notice.notice_type == 'open_to_collaborate':
            notice.open_to_collaborate_img_url = baseURL + 'ci-open-to-collaborate.png'
            notice.open_to_collaborate_svg_url = baseURL + 'ci-open-to-collaborate.svg'
            notice.open_to_collaborate_default_text = open_to_collaborate_text
        if notice.notice_type == 'attribution_incomplete':
            notice.attribution_incomplete_img_url = baseURL + 'ci-attribution-incomplete.png'
            notice.attribution_incomplete_svg_url = baseURL + 'ci-attribution-incomplete.svg'
            notice.attribution_incomplete_default_text = attribution_incomplete_text
        if notice.notice_type == 'open_to_collaborate_and_attribution_incomplete':
            notice.open_to_collaborate_img_url = baseURL + 'ci-open-to-collaborate.png'
            notice.open_to_collaborate_default_text = open_to_collaborate_text
            notice.attribution_incomplete_img_url = baseURL + 'ci-attribution-incomplete.png'
            notice.attribution_incomplete_svg_url = baseURL + 'ci-attribution-incomplete.svg'
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

# Helper function for creating/updating notices (institutions)
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


# Create/Update Notices (institutions)
def create_notices(selected_notices, institution, project, existing_notice, existing_inst_notice):
    # selected_notices would be a list: 
    # attribution_incomplete # open_to_collaborate # bcnotice # tknotice
    
    if existing_notice:
        existing_notice.delete()
    if existing_inst_notice:
        existing_inst_notice.delete()

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

