from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import generics, filters
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.viewsets import ViewSet

from .serializers import *
from projects.models import Project
from helpers.models import Notice
from projects.models import ProjectCreator

@api_view(['GET'])
def apiOverview(request, format=None):
    api_urls = {
        'projects_list': reverse('api-projects', request=request, format=format),
        'project_detail': '/projects/<PROJECT_UNIQUE_ID>/',
        'multi_project_detail':'/projects/multi/<PROJECT_UNIQUE_ID_1>,<PROJECT_UNIQUE_ID_2>/',
        'projects_by_user_id': '/projects/users/<USER_ID>/',
        'projects_by_institution_id': '/projects/institutions/<INSTITUTION_ID>/',
        'projects_by_researcher_id': '/projects/researchers/<RESEARCHER_ID>/',
        'open_to_collaborate_notice': reverse('api-open-to-collaborate', request=request, format=format),
        'api_documentation': 'https://github.com/biocodellc/localcontexts_db/wiki/API-Documentation',
        'usage_guide_notices': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-TK_BC-Notice-Usage-Guide_2021-11-16.pdf',
        'usage_guide_ci_notices': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-Institution-Notices-Usage-Guide_2021-11-16.pdf',
        'usage_guide_labels': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-TK_BC-Labels-Usage-Guide_2021-11-02.pdf',
    }
    return Response(api_urls)

@api_view(['GET'])
def openToCollaborateNotice(request):
    api_urls = {
        'notice_type': 'open_to_collaborate',
        'name': 'Open to Collaborate Notice',
        'default_text': 'Our institution is committed to the development of new modes of collaboration, engagement, and partnership with Indigenous peoples for the care and stewardship of past and future heritage collections.',
        'img_url': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/ci-open-to-collaborate.png',
        'svg_url': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/ci-open-to-collaborate.svg',
        'usage_guide_ci_notices': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-Institution-Notices-Usage-Guide_2021-11-16.pdf',
    }
    return Response(api_urls)

class ProjectList(generics.ListAPIView):
    queryset = Project.objects.exclude(project_privacy='Private')
    serializer_class = ProjectOverviewSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['^providers_id', '=unique_id', '$title']

    # '^' starts-with search
    # '=' exact matches
    # '$' regex search

class ProjectDetail(generics.RetrieveAPIView):
    lookup_field = 'unique_id'
    queryset = Project.objects.exclude(project_privacy='Private')

    def get_serializer_class(self):
        project = self.get_object()
        if Notice.objects.filter(project=project, archived=False).exists():
            return ProjectSerializer
        else:
            return ProjectNoNoticeSerializer

# TODO: Make this a filter instead?
@api_view(['GET'])
def project_detail_providers(request, providers_id):
    try:
        project = Project.objects.get(providers_id=providers_id)
        if project.project_privacy == 'Public' or project.project_privacy == 'Contributor':
            if project.has_notice():
                serializer = ProjectSerializer(project, many=False)
            else:
                serializer = ProjectNoNoticeSerializer(project, many=False)
            
            return Response(serializer.data)
        else:
            raise PermissionDenied({"message":"You don't have permission to view this project", "providers_id": providers_id})
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def projects_by_user(request, pk):
    try:
        user = User.objects.get(id=pk)
        projects = Project.objects.filter(project_creator=user).exclude(project_privacy='Private')
        serializer = ProjectOverviewSerializer(projects, many=True)
        return Response(serializer.data)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def projects_by_institution(request, institution_id, providers_id=None):
    try:
        institution = Institution.objects.get(id=institution_id)

        projects = []
        creators = ProjectCreator.objects.filter(institution=institution)
        for x in creators:
            projects.append(x.project)

        serializer = ProjectOverviewSerializer(projects, many=True)
        return Response(serializer.data)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def projects_by_researcher(request, researcher_id):
    try:
        researcher = Researcher.objects.get(id=researcher_id)

        projects = []
        creators = ProjectCreator.objects.filter(researcher=researcher)
        for x in creators:
            projects.append(x.project)

        serializers = ProjectOverviewSerializer(projects, many=True)
        return Response(serializers.data)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

class MultiProjectListDetail(ViewSet):

    def multisearch(self, request, unique_id):
        try:
            project = Project.objects.all()

            if unique_id is not None:
                unique_id = unique_id.split(',')
                query= Q()
                for x in unique_id:
                    q = Q(unique_id=x)
                    query |= q  
                project=project.filter(query).exclude(project_privacy='Private')
            notices = project.filter(Q(project_notice__isnull=False) & (Q(bc_labels__isnull=True) & Q(tk_labels__isnull=True))) 
            labels = project.filter(Q(bc_labels__isnull=False) | Q(tk_labels__isnull=False)).distinct()
            no_notice_labels = project.filter(Q(project_notice__isnull=True) & (Q(bc_labels__isnull=True) & Q(tk_labels__isnull=True))).distinct()

            notices_serializer = ProjectSerializer(notices, many=True)
            labels_serializer = ProjectNoNoticeSerializer(labels, many=True)
            no_notice_labels_serializer = ProjectNoNoticeSerializer(no_notice_labels, many=True)

            return Response({
                "notices_only":notices_serializer.data,
                "labels_only":labels_serializer.data,
                "no_labels_or_notices":no_notice_labels_serializer.data
            })
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

class CommunitySlugList(generics.ListAPIView):
    queryset = Community.objects.exclude(native_land_slug=None)
    serializer_class = CommunityNativeLandSlugSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['native_land_slug']