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
        'BCNotices': '/bcnotices/',
        'BCNotice Detail View': '/bcnotices/<str:unique_id>',
        'TKNotices': '/tknotices/',
        'TKNotice Detail View': '/tknotices/<str:unique_id>',
        'BCLabels': '/bclabels/',
        'BCLabel Detail View': '/bclabels/<str:unique_id>',
        'TKLabels': '/tklabels/',
        'TKLabel Detail View': '/tklabels/<str:unique_id>',
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
def bclabels(request):
    bclabels = BCLabel.objects.all()
    serializer = BCLabelSerializer(bclabels, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def bclabel_detail(request, unique_id):
    bclabel = BCLabel.objects.get(unique_id=unique_id)
    serializer = BCLabelSerializer(bclabel, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def tklabels(request):
    tklabels = TKLabel.objects.all()
    serializer = TKLabelSerializer(tklabels, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def tklabel_detail(request, unique_id):
    tklabel = TKLabel.objects.get(unique_id=unique_id)
    serializer = TKLabelSerializer(tklabel, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def projects(request):
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def project_detail(request, unique_id):
    projects = Project.objects.get(unique_id=unique_id)
    serializer = ProjectSerializer(projects, many=False)
    return Response(serializer.data)