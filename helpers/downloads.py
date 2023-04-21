from bclabels.models import BCLabel
from tklabels.models import TKLabel

from django.http import HttpResponse
from .utils import generate_zip, render_to_pdf
import requests

# Open to Collaborate Notice
def download_otc_notice():
    baseURL = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/'
    institution_text = "The Institution Notices are for use by collecting institutions, data repositories, researchers, and organizations who engage in collaborative curation with Indigenous and other marginalized communities who have been traditionally excluded from processes of documentation and record keeping.\nThe Institution Notices are intended to be displayed prominently on public-facing institutional websites, on digital collections pages and or in finding aids."

    # Initialize README TEXT
    readme_text = ''
    readme_text = institution_text + '\n\nThis folder contains the following files:\n'
    
    files = []

    open_to_collab_text = 'Our institution is committed to the development of new modes of collaboration, engagement, and partnership with Indigenous peoples for the care and stewardship of past and future heritage collections.'

    get_img = requests.get(baseURL + 'labels/notices/ci-open-to-collaborate.png')
    get_svg = requests.get(baseURL + 'labels/notices/ci-open-to-collaborate.svg')
    files.append(('Open_To_Collaborate' + '.png', get_img.content))
    files.append(('Open_To_Collaborate' + '.svg', get_svg.content))
    files.append(('Open_To_Collaborate' + '.txt', open_to_collab_text))

    # Create Readme
    file_names = []
    for f in files:
        file_names.append(f[0])
    readme_content = readme_text + '\n'.join(file_names) + '\n\nRefer to the Usage Guides (https://localcontexts.org/support/downloadable-resources/) for details on how to adapt and display the Open To Collaborate Notice.\n\nFor more information, contact Local Contexts at localcontexts.org or support@localcontexts.org'
    files.append(('README.txt', readme_content))

        # Generate zip file 
    full_zip_in_memory = generate_zip(files)

    zipfile_name = f"LC-Open_to_Collaborate_notice.zip"

    response = HttpResponse(full_zip_in_memory, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(zipfile_name)

    return response

# Download approved community Labels
def download_labels_zip(community):
    bclabels = BCLabel.objects.filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.filter(community=community, is_approved=True)

    template_path = 'snippets/pdfs/community-labels.html'
    context = {'community': community, 'bclabels': bclabels, 'tklabels': tklabels,}

    files = []

    # Add PDF to zip
    pdf = render_to_pdf(template_path, context)
    files.append(('Labels_Overview.pdf', pdf))

    # Add Label images, text and translations
    for bclabel in bclabels:
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
    for tklabel in tklabels:
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
    readme_text = "The Traditional Knowledge (TK) and Biocultural (BC) Labels reinforce the cultural authority and rights of Indigenous communities.\nThe TK and BC Labels are intended to be displayed prominently on public-facing Indigenous community, researcher and institutional websites, metadata and digital collection's pages.\n\nThis folder contains the following files:\n"
    file_names = []
    for f in files:
        file_names.append(f[0])
    readme_content = readme_text + '\n'.join(file_names) + '\n\nRefer to the Usage Guides (https://localcontexts.org/support/downloadable-resources/) for details on how to adapt and display the Labels for your community.\n\nFor more information, contact Local Contexts at localcontexts.org or support@localcontexts.org'
    files.append(('README.txt', readme_content))

    # Generate zip file 
    full_zip_in_memory = generate_zip(files)

    response = HttpResponse(full_zip_in_memory, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(community.community_name + '-Labels.zip')

    return response
