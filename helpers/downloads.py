from django.http import HttpResponse
import requests
from .utils import generate_zip

# Open to Collaborate Notice
def download_otc_notice(request):
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
