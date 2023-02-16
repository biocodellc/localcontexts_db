from api.base.views import *
from api.base import views as base_views
from rest_framework.views import APIView
from rest_framework.decorators import action
from . import serializers as v2_serializers
from rest_framework.viewsets import ViewSet
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated

class APIOverview(APIView):
    def get(self, request, format=None):
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

class OpenToCollaborateNotice(APIView):
    def get(self, request):
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
    # permission_classes = [HasAPIKey]
    queryset = Project.objects.exclude(project_privacy='Private')
    serializer_class = ProjectOverviewSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['^providers_id', '=unique_id', '$title']

    # '^' starts-with search
    # '=' exact matches
    # '$' regex search

class ProjectDetail(generics.RetrieveAPIView):
    # permission_classes = [HasAPIKey]
    lookup_field = 'unique_id'
    queryset = Project.objects.exclude(project_privacy='Private')

    def get_serializer_class(self):
        project = self.get_object()
        if Notice.objects.filter(project=project, archived=False).exists():
            return ProjectSerializer
        else:
            return ProjectNoNoticeSerializer

class ProjectsByIdViewSet(ViewSet):
    # permission_classes = [HasAPIKey | IsAuthenticated]
    def projects_by_user(self, request, pk):
        try:
            useracct = User.objects.get(id=pk)
            projects = Project.objects.filter(project_creator=useracct).exclude(project_privacy='Private')
            serializer = ProjectOverviewSerializer(projects, many=True)
            return Response(serializer.data)
            
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    def projects_by_institution(self, request, institution_id):
        try:
            institution = Institution.objects.get(id=institution_id)

            # print(request.search)

            projects = []
            creators = ProjectCreator.objects.filter(institution=institution)
            for x in creators:
                projects.append(x.project)

            serializer = ProjectOverviewSerializer(projects, many=True)

            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def projects_by_researcher(self, request, researcher_id):
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

    def project_detail_providers(self, request, providers_id):
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