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
            'all_notice_translations': '/notices/all_notice_translations',
            'api_documentation': 'https://github.com/biocodellc/localcontexts_db/wiki/API-Documentation',
            'usage_guides': 'https://localcontexts.org/support/downloadable-resources',
        }
        return Response(api_urls)

class NoticeDetails(ViewSet):
    permission_classes = [HasAPIKey]
    def open_To_Collaborate_Notice(self, request):
        OTCurls = {
            'notice_type': 'open_to_collaborate',
            'name': 'Open to Collaborate Notice',
            'default_text': 'Our institution is committed to the development of new modes of collaboration, engagement, and partnership with Indigenous peoples for the care and stewardship of past and future heritage collections.',
            'img_url': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/ci-open-to-collaborate.png',
            'svg_url': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/ci-open-to-collaborate.svg',
            'usage_guide_ci_notices': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-Institution-Notices-Usage-Guide_2021-11-16.pdf',
        }
        return Response(OTCurls)
    
    def all_Notice_Translations(self, request):
        OTCtranslations = [
            {
                'translated_name' : 'Abierto a Colaboración',
                'language_tag' : 'sp',
                'language' : 'Spanish',
                'translated_text' : 'Nuestra institución está comprometida a desarrollar nuevas formas de colaboración, participación y trabajo en conjunto con pueblos indígenas para el cuidado y manejo de colecciones patrimoniales pasadas y futuras.'
            },
            {
                'translated_name' : 'Ouverts à la collaboration',
                'language_tag' : 'fr',
                'language' : 'French',
                'translated_text' : 'Notre institution s’engage à développer de nouveaux modes de collaboration, d’engagement et de partenariat avec les peuples autochtones pour la conservation et la gestion des collections patrimoniales passées et futures.'
            },
            {
                'translated_name' : 'Kaupapa Whakangātahi',
                'language_tag' : 'mi',
                'language' : 'Māori',
                'translated_text' : 'E whakaū ana tō mātou wānanga i a ia anō, ki te pono me te tōtika kia whakamātauria ngā ara hou, me ngā ara pai me te āta tautiaki i ngā kohinga iwi taketake o mua, ā, ki tua o anamata.'
            }
        ]
        AItranslations = [
            {
                'translated_name' : 'Atribución Incompleta',
                'language_tag' : 'sp',
                'language' : 'Spanish',
                'translated_text' : 'Las colecciones y documentos en nuestra institución tienen atribuciones incompletas, imprecisas y/o faltantes. Utilizamos esta Notificación para identificar claramente este material y que pueda ser actualizado o corregido por las comunidades de origen. Nuestra institución está comprometida a llevar a cabo colaboraciones y alianzas para resolver este problema de atribuciones incorrectas o faltantes.'
            },
            {
                'translated_name' : 'Attribution Incomplète',
                'language_tag' : 'fr',
                'language' : 'French',
                'translated_text' : 'Certaines collections ou items dans nos institutions ont des attributions incomplètes, inexactes ou manquantes. Nous utilisons cette notification afin d’identifier clairement ce matériel pour qu’il soit mis à jour ou corrigé par les communautés d’origine. Notre institution s’est engagée à collaborer et à travailler en partenariat avec ces communautés afin de résoudre le problème d’attributions inexactes ou manquantes.'
            },
            {
                'translated_name' : 'Tutukinga Kore',
                'language_tag' : 'mi',
                'language' : 'Māori',
                'translated_text' : 'Tērā ngā kohinga me ngā taonga o tō mātou wānanga, kāore anō i tutuki, kua hē nei, kua ngaro nei rānei/hoki. Ko te tikanga o tēnei Pānui, he whakamōhio atu, me whakahou, me whakatika rānei tēnei taonga e ngā hapori, nāna tonu aua taonga. E ū ana tō mātou wānanga ki tēnei āhuatanga e rongoā ai ngā take nei nā.'
            }
        ]
        TKtranslations = [
            {
                'translated_name' : 'Notificación CT (Conocimiento Tradicional)',
                'language_tag' : 'sp',
                'language' : 'Spanish',
                'translated_text' : 'La Notificación de CT indica de manera visible que existen derechos y responsabilidades culturales asociados que requieren mayor atención en el caso de cualquier forma de uso y circulación futura de este material. La Notificación de CT tiene el potencial de indicar que Etiquetas de CT están siendo desarrolladas y su implementación está siendo negociada. Para mayor información sobre las Etiquetas CT por favor visitar https://localcontexts.org/notice/tk-notice/.'
            },
            {
                'translated_name' : 'Notification ST (Savoir Traditionnel)',
                'language_tag' : 'fr',
                'language' : 'French',
                'translated_text' : 'La notification ST sert à rendre visible l’information selon laquelle des droits culturels et des responsabilités sont rattachés au matériel en question et qu’une attention particulière doit être portée à tout partage ou toute utilisation future du matériel. La notification ST peut indiquer que les étiquettes ST (savoir traditionnel) sont en cours de réalisation et que leur application est en train d’être négociée. Pour plus d’information à propos des étiquettes ST, consulter le site https://localcontexts.org/notice/tk-notice/.'
            },
            {
                'translated_name' : 'Pānui Whakamārama TK',
                'language_tag' : 'mi',
                'language' : 'Māori',
                'translated_text' : 'Ko tā te Pānui Whakamārama TK, he āta whakaatu, tērā ētahi tikanga ā-iwi me ōna haepapa ki runga i te whakamahinga, i te horapatanga hoki o tēnei taonga. Kei roto hoki pea i tēnei Pānui TK, ko te kōrero e mea ana, tērā ngā Tohu TK e waihangatia ana, ā, kei te whiriwhirihia tonutia tōna whakatinanatanga. Mō ētahi atu kōrero mō ngā Pānui Whakamārama TK, pāwhiritia i konei.'
            }
        ]
        BCtranslations = [
            {
                'translated_name' : 'Notificación BC (Biocultural)',
                'language_tag' : 'sp',
                'language' : 'Spanish',
                'translated_text' : 'La Notificación BC indica de manera visible que hay derechos y responsabilidades culturales asociadas que necesitan mayor atención en caso de cualquier instancia en la que el material en cuestión es usado o compartido. La Notificación BC reconoce los derechos de personas y comunidades Indígenas para definir las circunstancias bajo las cuales permitir el uso de información, colecciones, datos, e información de secuencia digital generada desde las formas de biodiversidad y recursos genéticos asociados con tierras, aguas y territorios tradicionales/ancestrales. La Notificación BC indica que las Etiquetas BC (Bioculturales) están en desarrollo y que su implementación está siendo negociada. Para mayor información sobre las Etiquetas BC por favor visitar https://localcontexts.org/notices/biocultural-notices/.'
            },
            {
                'translated_name' : 'Notification BC (Bioculturelle)',
                'language_tag' : 'fr',
                'language' : 'French',
                'translated_text' : 'La notification BC sert à rendre visible l’information selon laquelle le matériel utilisé est accompagné de droits culturels et de responsabilités qui nécessitent une attention particulière au moment de le partager ou de l’utiliser. La notification BC est une reconnaissance des droits des peuples autochtones de permettre l’utilisation d’informations, de collections, de données et d’informations sur les séquences numériques provenant de la biodiversité et des ressources associées à leurs terres, cours d’eau et territoires traditionnels. La notification BC peut indiquer que les étiquettes BC (bioculturelles) sont en cours de réalisation et que leur application est en train d’être négociée. Pour plus d’information à propos des étiquettes BC, consulter le site https://localcontexts.org/notices/biocultural-notices/.'
            },
            {
                'translated_name' : 'Pānui Whakamārama BC',
                'language_tag' : 'mi',
                'language' : 'Māori',
                'translated_text' : 'Ko tā te Pānui Whakamārama BC, he āta whakaatu, tērā ētahi tikanga ā-iwi me ōna haepapa ki runga i te whakamahinga, i te horapatanga hoki o tēnei taonga me ōna raraunga rānei. Whakamanahia ai ki tēnei Pānui Whakamārama BC, ko te mana tuku iho o ngā iwi taketake ki roto i ngā kohinga mātauranga pūtaiao, me ngā raraunga hangarau mō runga i ngā hapori, ngā tāngata, me te rerenga rauropi e noho pū ana i ngā whenua, i ngā wai me ngā rohe o ngā iwi taketake. Kei roto hoki pea i tēnei Pānui BC, ko te kōrero e mea ana, tērā ngā Tohu BC (Rerenga rauropi) e waihangatia ana, ā, kei te whiriwhirihia tonutia tōna whakatinanatanga. Mō ētahi atu kōrero mō ngā Pānui Whakamārama BC, pāwhiritia i konei.'
            }
        ]

        OTC = {
            'name': 'Open to Collaborate Notice',
            'notice_type': 'open_to_collaborate',
            'language_tag': 'en',
            'language': 'English',
            'default_text': 'Our institution is committed to the development of new modes of collaboration, engagement, and partnership with Indigenous peoples for the care and stewardship of past and future heritage collections.',
            'img_url': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/ci-open-to-collaborate.png',
            'svg_url': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/ci-open-to-collaborate.svg',
            'translations': OTCtranslations
        }
        
        AI = {
            'name': 'Attribution Incomplete Notice',
            'notice_type': 'attribution_incomplete',
            'language_tag': 'en',
            'language': 'English',
            'default_text': 'Collections and items in our institution have incomplete, inaccurate, and/or missing attribution. We are using this notice to clearly identify this material so that it can be updated, or corrected by communities of origin. Our institution is committed to collaboration and partnerships to address this problem of incorrect or missing attribution.',
            'img_url': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/ci-attribution-incomplete.png',
            'svg_url': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/ci-attribution-incomplete.svg',
            'translations': AItranslations

        }
        TK = {
            'name': 'Traditional Knowledge (TK) Notice',
            'notice_type': 'traditional_knowledge',
            'language_tag': 'en',
            'language': 'English',
            'default_text': 'The TK (Traditional Knowledge) Notice is a visible notification that there are accompanying cultural rights and responsibilities that need further attention for any future sharing and use of this material. The TK Notice may indicate that TK Labels are in development and their implementation is being negotiated.',
            'img_url': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/tk-notice.png',
            'svg_url': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/tk-notice.svg',
            'translations': TKtranslations
        }
        BC = {
            'name': 'Biocultural (BC) Notice',
            'notice_type': 'biocultural',
            'language_tag': 'en',
            'language': 'English',
            'default_text': 'The BC (Biocultural) Notice is a visible notification that there are accompanying cultural rights and responsibilities that need further attention for any future sharing and use of this material or data. The BC Notice recognizes the rights of Indigenous peoples to permission the use of information, collections, data and digital sequence information (DSI) generated from the biodiversity or genetic resources associated with traditional lands, waters, and territories. The BC Notice may indicate that BC Labels are in development and their implementation is being negotiated.',
            'img_url': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/bc-notice.png',
            'svg_url': 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/bc-notice.svg',
            'translations': BCtranslations
        }

        noticeTranslationURLs = {
            'usage_guides': 'https://localcontexts.org/support/downloadable-resources/',
            'notice' : [OTC, AI, TK, BC]
        }
        return Response(noticeTranslationURLs)

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

#TODO: remove this function or convert it so that the project detail (list view) can be used using either projectID or providersID. Two URLs that use one call. projects/external url would be removed
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

