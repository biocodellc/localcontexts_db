from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Project
from helpers.utils import render_to_pdf, generate_zip
from django.http import HttpResponse
import urllib

def view_project(request, unique_id):
    project = Project.objects.get(unique_id=unique_id)
    return render(request, 'projects/view-project.html', {'project': project})

def download_project_zip(request, unique_id):
    project = Project.objects.get(unique_id=unique_id)
    template_path = 'snippets/pdfs/project-pdf.html'
    context = {'project': project}

    files = []

    # Create PDF from project context, append to files list
    pdf = render_to_pdf(template_path, context)
    files.append((project.title + ".pdf", pdf))

# TODO: fix this
    # Use instructions location
    # url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-TK_BC-Notice-Usage-Guide_2021-11-16.pdf'
    # res = urllib.request.urlretrieve(url)
    # contents = open(res[0]).read()
    # f = open('LC-TK_BC-Notice-Usage-Guide_2021-11-16.pdf.pdf','w')
    # f.write(contents)
    # f.close()
    # files.append("use_guide.pdf", f)

    full_zip_in_memory = generate_zip(files)

    response = HttpResponse(full_zip_in_memory, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format('project.zip')

    return response