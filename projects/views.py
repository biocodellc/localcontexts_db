from django.shortcuts import render, redirect
from .models import Project

def view_project(request, unique_id):
    project = Project.objects.get(unique_id=unique_id)
    return render(request, 'projects/view-project.html', {'project': project})
