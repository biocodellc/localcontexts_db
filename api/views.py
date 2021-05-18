from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .serializers import *
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from projects.models import Project

@api_view(['GET'])
def apiOverview(request):
    # TODO: Project should be unique_id not pk
    api_urls = {
        'BCLabels': '/bclabels/',
        'BCLabel Detail View': '/bclabel/<str:unique_id>',
        'TKLabels': '/tklabels/',
        'TKLabel Detail View': '/tklabel/<str:unique_id>',
        'Projects': '/projects/',
        'Project Detail View': '/project/<str:pk>',
    }
    return Response(api_urls)

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
def project_detail(request, pk):
    # TODO: Project should be unique_id not pk
    projects = Project.objects.get(id=pk)
    serializer = ProjectSerializer(projects, many=False)
    return Response(serializer.data)