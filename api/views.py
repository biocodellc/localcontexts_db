from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .serializers import *
from bclabels.models import BCLabel, BCNotice
from tklabels.models import TKLabel, TKNotice
from projects.models import Project

@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'Projects': '/projects',
        'Project detail view': '/projects/<str:unique_id>',
        'Projects by user': '/projects/users/<str:username>',
        'Projects by institution': '/projects/institutions/<str:institution_id>',
        'Projects by researcher': 'projects/researchers/<str:researcher_id>',
    }
    return Response(api_urls)

@api_view(['GET'])
def projects(request):
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def project_detail(request, unique_id):
    project = Project.objects.get(unique_id=unique_id)
    serializer = ProjectSerializer(project, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def projects_by_user(request, username):
    user = User.objects.get(username=username)
    projects = Project.objects.filter(project_creator=user)
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def projects_by_institution(request, institution_id):
    institution = Institution.objects.get(id=institution_id)
    projects = institution.projects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def projects_by_researcher(request, researcher_id):
    researcher = Researcher.objects.get(id=researcher_id)
    projects = researcher.projects.all()
    serializers = ProjectSerializer(projects, many=True)
    return Response(serializers.data)

