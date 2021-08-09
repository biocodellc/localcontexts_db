from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Project

@login_required(login_url='login')
def view_project(request, unique_id):
    project = Project.objects.get(unique_id=unique_id)
    return render(request, 'projects/view-project.html', {'project': project})