from django.shortcuts import render, redirect
from .models import Project, ProjectContributors, ProjectCreator, ProjectPerson
from helpers.models import Notice
from helpers.utils import render_to_pdf, generate_zip
from django.http import HttpResponse, Http404
import requests
from accounts.models import UserAffiliation
from researchers.models import Researcher
from researchers.utils import is_user_researcher

def view_project(request, unique_id):
    try:
        project = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').get(unique_id=unique_id)
        sub_projects = Project.objects.filter(source_project_uuid=project.unique_id).values_list('unique_id', 'title')
        notices = Notice.objects.filter(project=project, archived=False)
        creator = ProjectCreator.objects.get(project=project)
        communities = None
        institutions = None
        user_researcher = Researcher.objects.none()

        #  If user is logged in AND belongs to account of a contributor
        if request.user.is_authenticated:
            affiliations = UserAffiliation.objects.get(user=request.user)

            community_ids = ProjectContributors.objects.filter(project=project).values_list('communities__id', flat=True)
            institution_ids = ProjectContributors.objects.filter(project=project).values_list('institutions__id', flat=True)
            communities = affiliations.communities.filter(id__in=community_ids)
            institutions = affiliations.institutions.filter(id__in=institution_ids)

            researcher_ids = ProjectContributors.objects.filter(project=project).values_list('researchers__id', flat=True)

            if Researcher.objects.filter(user=request.user).exists():
                researcher = Researcher.objects.get(user=request.user)
                researchers = Researcher.objects.filter(id__in=researcher_ids)
                if researcher in researchers:
                    user_researcher = Researcher.objects.get(id=researcher.id)
                
        context = {
            'project': project, 
            'notices': notices,
            'creator': creator,
            'communities': communities,
            'institutions': institutions,
            'user_researcher': user_researcher,
            'sub_projects': sub_projects,
        }

        if project.project_privacy == 'Private':
            if request.user.is_authenticated:
                return render(request, 'projects/view-project.html', context)
            else:
                return redirect('login')
        else:
            return render(request, 'projects/view-project.html', context)
    except:
        raise Http404()


def download_project_zip(request, unique_id):
    try:
        baseURL = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/'
        project = Project.objects.prefetch_related('bc_labels', 'tk_labels').get(unique_id=unique_id)
        project_bclabels = project.bc_labels.all()
        project_tklabels = project.tk_labels.all()
        project_creator = ProjectCreator.objects.get(project=project)
        contributors = ProjectContributors.objects.prefetch_related('communities', 'institutions', 'researchers').get(project=project)
        project_people = ProjectPerson.objects.filter(project=project)

        notice_exists = Notice.objects.filter(project=project).exists()

        template_path = 'snippets/pdfs/project-pdf.html'
        context = { 'project': project, 'project_creator': project_creator, 'contributors': contributors, 'project_people': project_people }

        files = []

        # Initialize README TEXT
        readme_text = ''

        # Set README text if both types of notice present
        if notice_exists:
            institution_text = "The Institution Notices are for use by collecting institutions, data repositories and organizations who engage in collaborative curation with Indigenous and other marginalized communities who have been traditionally excluded from processes of documentation and record keeping.\nThe Institution Notices are intended to be displayed prominently on public-facing institutional websites, on digital collections pages and or in finding aids."
            notice_text = "The BC, TK and Attribution Incomplete Notices are specific tools for institutions and researchers which support the recognition of Indigenous interests in collections and data. The Notices are a mechanism for researchers and institutional staff to identify Indigenous collections and Indigenous interests in data.\n\nThe Notices can function as place-holders on collections, data, or in a sample field until a TK or a BC Label is added by a community."
            readme_text = notice_text + '\n\n' + institution_text + '\n\nThis folder contains the following files:\n'

        # Create PDF from project context, append to files list
        pdf = render_to_pdf(template_path, context)
        files.append(('Project_Overview.pdf', pdf))

        # Label / Notice Files
        if notice_exists:
            notices = Notice.objects.filter(project=project)
            for notice in notices:
                if not notice.archived:
                    # Add Usage Guide
                    usage_guide_url = baseURL + 'guides/LC-TK_BC-Notice-Usage-Guide_2021-11-16.pdf'
                    response = requests.get(usage_guide_url) 
                    files.append(('Notices_Usage_Guide.pdf', response.content))

                    # Create PNG and TXT files based on which Notices are attached to the Project
                    if notice.notice_type == 'biocultural':
                        get_img = requests.get(notice.img_url)
                        get_svg = requests.get(baseURL + 'labels/notices/bc-notice.svg')
                        files.append(('Biocultural_Notice' + '.png', get_img.content))
                        files.append(('Biocultural_Notice' + '.svg', get_svg.content))
                        files.append(('Biocultural_Notice' + '.txt', notice.default_text))

                    if notice.notice_type == 'traditional_knowledge':
                        get_img = requests.get(notice.img_url)
                        get_svg = requests.get(baseURL + 'labels/notices/tk-notice.svg')
                        files.append(('Traditional_Knowledge_Notice' + '.png', get_img.content))
                        files.append(('Traditional_Knowledge_Notice' + '.svg', get_svg.content))
                        files.append(('Traditional_Knowledge_Notice' + '.txt', notice.default_text))
                    
                    if notice.notice_type == 'attribution_incomplete':
                        get_img = requests.get(notice.img_url)
                        get_svg = requests.get(baseURL + 'labels/notices/ci-attribution-incomplete.svg')
                        files.append(('Attribution_Incomplete' + '.png', get_img.content))
                        files.append(('Attribution_Incomplete' + '.svg', get_svg.content))
                        files.append(('Attribution_Incomplete' + '.txt', notice.default_text))

        if project_bclabels or project_tklabels:
            # Labels Usage guide PDF
            usage_guide_url = baseURL + 'guides/LC-TK_BC-Labels-Usage-Guide_2021-11-02.pdf'
            response = requests.get(usage_guide_url) 
            files.append(('BC_TK_Label_Usage_Guide.pdf', response.content))

            # Set readme text
            readme_text = "The Traditional Knowledge (TK) and Biocultural (BC) Labels reinforce the cultural authority and rights of Indigenous communities. \nThe TK and BC Labels are intended to be displayed prominently on public-facing Indigenous community, researcher and institutional websites, metadata and digital collection's pages.\n\nThis folder contains the following files:\n"

        # Add Label images, text and translations
        for bclabel in project_bclabels:
            get_image = requests.get(bclabel.img_url)
            get_svg = requests.get(bclabel.svg_url)
            files.append((bclabel.name + '.png', get_image.content))
            files.append((bclabel.name + '.svg', get_svg.content))

            # Default Label text
            text_content = bclabel.name + '\n' + bclabel.label_text
            text_addon = []

            if bclabel.bclabel_translation.all():
                for translation in bclabel.bclabel_translation.all():
                    text_addon.append('\n\n' + translation.translated_name + ' (' + translation.language + ') ' + '\n' + translation.translated_text)
                files.append((bclabel.name + '.txt', text_content + '\n'.join(text_addon)))
            else:
                files.append((bclabel.name + '.txt', text_content))

        # Add Label images, text and translations
        for tklabel in project_tklabels:
            get_image = requests.get(tklabel.img_url)
            get_svg = requests.get(tklabel.svg_url)
            files.append((tklabel.name + '.png', get_image.content))
            files.append((tklabel.name + '.svg', get_svg.content))
            
            # Default Label text
            text_content = tklabel.name + '\n' + tklabel.label_text
            text_addon = []

            if tklabel.tklabel_translation.all():
                for translation in tklabel.tklabel_translation.all():
                    text_addon.append('\n\n' + translation.translated_name + ' (' + translation.language + ') ' + '\n' + translation.translated_text)
                files.append((tklabel.name + '.txt', text_content + '\n'.join(text_addon)))
            else:
                files.append((tklabel.name + '.txt', text_content))
        
        # Create Readme
        file_names = []
        for f in files:
            file_names.append(f[0])
        readme_content = readme_text + '\n'.join(file_names) + '\n\nRefer to the Usage Guide for details on how to adapt and display the Notices or Labels for your Project.\n\nFor more information, contact Local Contexts at localcontexts.org or support@localcontexts.org'
        files.append(('README.txt', readme_content))

        # Generate zip file 
        full_zip_in_memory = generate_zip(files)

        zipfile_name = f"LC-Project-{project.title}.zip"

        response = HttpResponse(full_zip_in_memory, content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(zipfile_name)

        return response
    except:
        raise Http404()