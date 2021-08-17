from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from .serializers import *
from bclabels.models import BCLabel, BCNotice
from tklabels.models import TKLabel, TKNotice
from projects.models import Project

@api_view(['GET'])
def apiOverview(request, format=None):
    api_urls = {
        'projects': reverse('api-projects', request=request, format=format),
        'project detail view': '/projects/<PROJECT_UNIQUE_ID>',
        'projects by username': '/projects/users/<USERNAME>',
        'projects by institution id': '/projects/institutions/<INSTITUTION_ID>',
        'projects by researcher id': '/projects/researchers/<RESEARCHER_ID>',
    }
    return Response(api_urls)

@api_view(['GET'])
def projects(request):
    projects = Project.objects.filter(is_discoverable=True, is_public=True)
    serializer = ProjectOverviewSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def project_detail(request, unique_id):
    project = Project.objects.get(unique_id=unique_id)
    if project.is_public:
        serializer = ProjectSerializer(project, many=False)
        return Response(serializer.data)
    else:
        raise PermissionDenied({"message":"You don't have permission to view this project",
                                "unique_id": unique_id})

@api_view(['GET'])
def projects_by_user(request, username):
    user = User.objects.get(username=username)
    projects = Project.objects.filter(project_creator=user, is_discoverable=True, is_public=True)
    serializer = ProjectOverviewSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def projects_by_institution(request, institution_id):
    institution = Institution.objects.get(id=institution_id)
    projects = institution.projects.filter(is_discoverable=True, is_public=True)
    serializer = ProjectOverviewSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def projects_by_researcher(request, researcher_id):
    researcher = Researcher.objects.get(id=researcher_id)
    projects = researcher.projects.filter(is_discoverable=True, is_public=True)
    serializers = ProjectOverviewSerializer(projects, many=True)
    return Response(serializers.data)

