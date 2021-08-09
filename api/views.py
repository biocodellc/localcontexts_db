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
        'Projects': '/projects/',
        'Project Detail View': '/projects/<str:unique_id>',
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