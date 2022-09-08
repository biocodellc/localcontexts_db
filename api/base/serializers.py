from django.db.models import fields
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from helpers.models import LabelTranslation, Notice
from projects.models import Project, ProjectCreator
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from django.contrib.auth.models import User

class InstitutionSerializer(serializers.ModelSerializer):
    institution_name = SerializerMethodField()

    class Meta:
        model = Institution
        fields = ('id', 'institution_name')

    def get_institution_name(self, obj):
        return str(obj.institution_name)

class ResearcherSerializer(serializers.ModelSerializer):
    user = SerializerMethodField()

    class Meta:
        model = Researcher
        fields = ('id', 'user', 'orcid')

    def get_user(self, obj):
        if obj.user.first_name and obj.user.last_name:
            return str(obj.user.first_name) + ' ' + str(obj.user.last_name)
        else:
            return str(obj.user.username)

class LabelTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabelTranslation
        fields = ('translated_name', 'language_tag', 'language', 'translated_text')
    
class BCLabelSerializer(serializers.ModelSerializer):
    community = SerializerMethodField()
    translations = LabelTranslationSerializer(source="bclabel_translation", many=True)

    class Meta:
        model = BCLabel
        fields = ('unique_id', 'name', 'label_type', 'language_tag', 'language', 'label_text', 'img_url', 'svg_url', 'audiofile',  'community', 'translations', 'created', 'updated')
    
    def get_community(self, obj):
        return str(obj.community.community_name)

class TKLabelSerializer(serializers.ModelSerializer):
    community = SerializerMethodField()
    translations = LabelTranslationSerializer(source="tklabel_translation", many=True)

    class Meta:
        model = TKLabel
        fields = ('unique_id', 'name', 'label_type', 'language_tag', 'language', 'label_text', 'img_url', 'svg_url', 'audiofile', 'community', 'translations', 'created', 'updated')

    def get_community(self, obj):
        return str(obj.community.community_name)

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ('notice_type', 'name', 'img_url', 'svg_url', 'default_text', 'created', 'updated',)

class ProjectOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('unique_id', 'providers_id', 'title', 'project_privacy', 'date_added', 'date_modified',)

class ProjectCreatorSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer()
    researcher = ResearcherSerializer()
    community = SerializerMethodField()

    class Meta:
        model = ProjectCreator
        fields = ('institution', 'researcher', 'community')
    
    def get_community(self, obj):
        if obj.community: 
            return str(obj.community.community_name)

# Notices only   
class ProjectSerializer(serializers.ModelSerializer):
    created_by = ProjectCreatorSerializer(source="project_creator_project", many=True)
    notice = NoticeSerializer(source="project_notice", many=True)

    class Meta:
        model = Project
        fields = ('unique_id', 'providers_id', 'project_page', 'title', 'project_privacy', 'date_added', 'date_modified', 'created_by', 'notice', 'project_boundary_geojson')

# Labels only
class ProjectNoNoticeSerializer(serializers.ModelSerializer):
    created_by = ProjectCreatorSerializer(source="project_creator_project", many=True)
    bc_labels = BCLabelSerializer(many=True)
    tk_labels = TKLabelSerializer(many=True)

    class Meta:
        model = Project
        fields = ('unique_id', 'providers_id', 'project_page', 'title', 'project_privacy', 'date_added', 'date_modified', 'created_by', 'bc_labels', 'tk_labels', 'project_boundary_geojson')
