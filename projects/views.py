from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Project
from helpers.utils import render_to_pdf, generate_zip
from django.http import HttpResponse
import requests

def view_project(request, unique_id):
    project = Project.objects.get(unique_id=unique_id)
    return render(request, 'projects/view-project.html', {'project': project})

# TODO: Images need to be SVGs
def download_project_zip(request, unique_id):
    project = Project.objects.get(unique_id=unique_id)
    project_bclabels = project.bc_labels.all()
    project_tklabels = project.tk_labels.all()

    template_path = 'snippets/pdfs/project-pdf.html'
    context = {'project': project}

    files = []

    # Create PDF from project context, append to files list
    pdf = render_to_pdf(template_path, context)
    files.append(('Project_Overview.pdf', pdf))

    # Label / Notice Files
    for notice in project.project_notice.all():
        if not notice.archived:
            # Add Usage Guide
            usage_guide_url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-TK_BC-Notice-Usage-Guide_2021-11-16.pdf'
            response = requests.get(usage_guide_url) 
            files.append(('TK_BC_Notice_Usage_Guide.pdf', response.content))

            # Create PNG and TXT files based on which Notices are attached to the Project
            if notice.notice_type == 'biocultural':
                get_img = requests.get(notice.bc_img_url)
                files.append(('Biocultural_Notice' + '.png', get_img.content))
                files.append(('Biocultural_Notice' + '.txt', notice.bc_default_text))

            if notice.notice_type == 'traditional_knowledge':
                get_img = requests.get(notice.tk_img_url)
                files.append(('Traditional_Knowledge_Notice' + '.png', get_img.content))
                files.append(('Traditional_Knowledge_Notice' + '.txt', notice.tk_default_text))

            if notice.notice_type == 'biocultural_and_traditional_knowledge':
                get_bc_img = requests.get(notice.bc_img_url)
                get_tk_img = requests.get(notice.tk_img_url)
                files.append(('Biocultural_Notice' + '.png', get_bc_img.content))
                files.append(('Traditional_Knowledge_Notice' + '.png', get_tk_img.content))
                files.append(('Biocultural_Notice' + '.txt', notice.bc_default_text))
                files.append(('Traditional_Knowledge_Notice' + '.txt', notice.tk_default_text))


    # Institution notices
    for inst_notice in project.project_institutional_notice.all():
        if not inst_notice.archived:
            # Add Usage Guide
            usage_guide_url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-Institution-Notices-Usage-Guide_2021-11-16.pdf'
            response = requests.get(usage_guide_url) 
            files.append(('Institution_Notice_Usage_Guide.pdf', response.content))

            # Create PNG and TXT files based on which Notices are attached to the Project
            if inst_notice.notice_type == 'open_to_collaborate':
                get_img = requests.get(inst_notice.open_to_collaborate_img_url)
                files.append(('Open_To_Collaborate' + '.png', get_img.content))
                files.append(('Open_To_Collaborate' + '.txt', inst_notice.open_to_collaborate_default_text))

            if inst_notice.notice_type == 'attribution_incomplete':
                get_img = requests.get(inst_notice.attribution_incomplete_img_url)
                files.append(('Attribution_Incomplete' + '.png', get_img.content))
                files.append(('Attribution_Incomplete' + '.txt', inst_notice.attribution_incomplete_default_text))

            if inst_notice.notice_type == 'open_to_collaborate_and_attribution_incomplete':
                get_open_img = requests.get(inst_notice.open_to_collaborate_img_url)
                get_attr_img = requests.get(inst_notice.attribution_incomplete_img_url)
                files.append(('Open_To_Collaborate' + '.png', get_open_img.content))
                files.append(('Attribution_Incomplete' + '.png', get_attr_img.content))
                files.append(('Open_To_Collaborate' + '.txt', inst_notice.open_to_collaborate_default_text))
                files.append(('Attribution_Incomplete' + '.txt', inst_notice.attribution_incomplete_default_text))

    if project_bclabels or project_tklabels:
        # Labels Usage guide PDF
        usage_guide_url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-TK_BC-Labels-Usage-Guide_2021-11-02.pdf'
        response = requests.get(usage_guide_url) 
        files.append(('BC_TK_Label_Usage_Guide.pdf', response.content))

    # Add Label images, text and translations
    for bclabel in project_bclabels:
        get_image = requests.get(bclabel.img_url)
        files.append((bclabel.name + '.png', get_image.content))

        # Default Label text
        text_content = bclabel.name + '\n' + bclabel.default_text
        text_addon = []

        if bclabel.bclabel_translation.all():
            for translation in bclabel.bclabel_translation.all():
                text_addon.append('\n\n' + translation.title + ' (' + translation.language + ') ' + '\n' + translation.translation)
            files.append((bclabel.name + '.txt', text_content + '\n'.join(text_addon)))
        else:
            files.append((bclabel.name + '.txt', text_content))

    # Add Label images, text and translations
    for tklabel in project_tklabels:
        get_image = requests.get(tklabel.img_url)
        files.append((tklabel.name + '.png', get_image.content))
        
        # Default Label text
        text_content = tklabel.name + '\n' + tklabel.default_text
        text_addon = []

        if tklabel.tklabel_translation.all():
            for translation in tklabel.tklabel_translation.all():
                text_addon.append('\n\n' + translation.title + ' (' + translation.language + ') ' + '\n' + translation.translation)
            files.append((tklabel.name + '.txt', text_content + '\n'.join(text_addon)))
        else:
            files.append((tklabel.name + '.txt', text_content))
    
    # Create Readme
    readme_text = 'This folder contains the following files:\n'
    file_names = []
    for f in files:
        file_names.append(f[0])
    readme_content = readme_text + '\n'.join(file_names) + '\n\nRefer to the Usage Guide for details on how to adapt and display the Notices or Labels for your Project.\n\nFor more information, contact Local Contexts at http://localcontexts.org or support@localcontexts.org'
    files.append(('README.txt', readme_content))

    # Generate zip file 
    full_zip_in_memory = generate_zip(files)

    response = HttpResponse(full_zip_in_memory, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format('LC-Project.zip')

    return response