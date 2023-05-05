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
            'server': reverse('api-overview', request=request, format=format),
            'projects_list': '/projects/',
            'project_detail': '/projects/<PROJECT_UNIQUE_ID>/',
            'multi_project_detail':'/projects/multi/<PROJECT_UNIQUE_ID_1>,<PROJECT_UNIQUE_ID_2>/',
            'projects_by_user_id': '/projects/users/<USER_ID>/',
            'projects_by_institution_id': '/projects/institutions/<INSTITUTION_ID>/',
            'projects_by_researcher_id': '/projects/researchers/<RESEARCHER_ID>/',
            'open_to_collaborate_notice': '/notices/open_to_collaborate/',
            'api_documentation': 'https://github.com/biocodellc/localcontexts_db/wiki/API-Documentation',
            'usage_guides': 'https://localcontexts.org/support/downloadable-resources',
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
    permission_classes = [HasAPIKey]
    queryset = Project.objects.exclude(project_privacy='Private')
    serializer_class = ProjectOverviewSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['^providers_id', '=unique_id', '$title']

    # '^' starts-with search
    # '=' exact matches
    # '$' regex search

class ProjectDetail(generics.RetrieveAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    lookup_field = 'unique_id'
    queryset = Project.objects.exclude(project_privacy='Private')

    def get_serializer_class(self):
        project = self.get_object()
        if Notice.objects.filter(project=project, archived=False).exists():
            return ProjectSerializer
        else:
            return ProjectNoNoticeSerializer
    
    def get_object(self):
        try:
            unique_id = self.kwargs.get('unique_id')
            obj = self.queryset.get(unique_id=unique_id)
            return obj
        except Project.DoesNotExist:
            raise Http404("Project does not exist")

class ProjectsByIdViewSet(ViewSet):
    permission_classes = [HasAPIKey | IsAuthenticated]
    def projects_by_user(self, request, pk):
        try:
            useracct = User.objects.get(id=pk)
            projects = Project.objects.filter(project_creator=useracct).exclude(project_privacy='Private')
            serializer = ProjectOverviewSerializer(projects, many=True)
            return Response(serializer.data)
            
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def projects_by_institution(self, request, institution_id, providers_id=None):
        try:
            institution = Institution.objects.get(id=institution_id)

            projects = []
            creators = ProjectCreator.objects.filter(institution=institution)
            if providers_id != None:
                for x in creators:
                    if x.project.providers_id == providers_id:
                        projects.append(x.project)
            else:
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

#ASHLEYTODO: remove this function or convert it so that the project detail (list view) can be used using either projectID or providersID. Two URLs that use one call. projects/external url would be removed
# Make this a filter instead?
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
        
class MultiProjectListDetail(ViewSet):
    permission_classes = [HasAPIKey | IsAuthenticated]

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
    
    def multisearch_date(self, request, unique_id):
        try:
            project = Project.objects.all()

            if unique_id is not None:
                unique_id = unique_id.split(',')
                query= Q()
                for x in unique_id:
                    q = Q(unique_id=x)
                    query |= q  
                project=project.filter(query).exclude(project_privacy='Private')

            serializer = ProjectDateModified(project, many=True)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)