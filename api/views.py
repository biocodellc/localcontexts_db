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
        # 'BCNotices': '/bcnotices/',
        # 'BCNotice Detail View': '/bcnotices/<str:unique_id>',
        # 'TKNotices': '/tknotices/',
        # 'TKNotice Detail View': '/tknotices/<str:unique_id>',
        'Projects': '/projects/',
        'Project Detail View': '/projects/<str:unique_id>',
    }
    return Response(api_urls)

@api_view(['GET'])
def bcnotices(request):
    bcnotices = BCNotice.objects.all()
    serializer = BCNoticeSerializer(bcnotices, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def bcnotice_detail(request, unique_id):
    bcnotice = BCNotice.objects.get(unique_id=unique_id)
    serializer = BCNoticeSerializer(bcnotice, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def tknotices(request):
    tknotices = TKNotice.objects.all()
    serializer = TKNoticeSerializer(tknotices, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def tknotice_detail(request, unique_id):
    tknotice = TKNotice.objects.get(unique_id=unique_id)
    serializer = TKNoticeSerializer(tknotice, many=False)
    return Response(serializer.data)

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