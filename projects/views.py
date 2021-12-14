from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Project
from helpers.utils import render_to_pdf, generate_zip
from django.http import HttpResponse
import requests

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
    # files.append((project.title + ".pdf", pdf))
    files.append(("Project_Overview.pdf", pdf))

    # Usage guide PDF
    usage_guide_url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-TK_BC-Notice-Usage-Guide_2021-11-16.pdf'
    response = requests.get(usage_guide_url) 
    files.append(('BC_TK_Label_Usage_Guide.pdf', response.content))

    # TODO: 
    # Label or Notice SVGs and .txt files
    # README.txt

    # Generate zip file 
    full_zip_in_memory = generate_zip(files)

    response = HttpResponse(full_zip_in_memory, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format('project.zip')

    return response