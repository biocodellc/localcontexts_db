from django.db.models import fields
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from helpers.models import LabelTranslation, Notice, InstitutionNotice
from projects.models import Project
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
        return str(obj.user.first_name) + ' ' + str(obj.user.last_name)

class LabelTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabelTranslation
        fields = ('title', 'language_tag', 'language', 'translation')
    
class BCLabelSerializer(serializers.ModelSerializer):
    community = SerializerMethodField()
    translations = LabelTranslationSerializer(source="bclabel_translation", many=True)

    class Meta:
        model = BCLabel
        fields = ('name', 'label_type', 'language_tag', 'language', 'default_text', 'img_url', 'svg_url', 'community', 'translations', 'created', 'updated')
    
    def get_community(self, obj):
        return str(obj.community.community_name)

class TKLabelSerializer(serializers.ModelSerializer):
    community = SerializerMethodField()
    translations = LabelTranslationSerializer(source="tklabel_translation", many=True)

    class Meta:
        model = TKLabel
        fields = ('name', 'label_type', 'language_tag', 'language', 'default_text', 'img_url', 'svg_url', 'community', 'translations', 'created', 'updated')

    def get_community(self, obj):
        return str(obj.community.community_name)

class NoticeSerializer(serializers.ModelSerializer):
    placed_by_institution = InstitutionSerializer()
    placed_by_researcher = ResearcherSerializer()

    class Meta:
        model = Notice
        fields = ('notice_type', 'bc_img_url', 'bc_svg_url', 'bc_default_text', 'tk_img_url', 'tk_svg_url', 'tk_default_text', 'placed_by_researcher', 'placed_by_institution', 'created', 'updated',)

class InstitutionNoticeSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer()

    class Meta:
        model = InstitutionNotice
        fields = ('notice_type', 'institution', 'open_to_collaborate_img_url', 'open_to_collaborate_svg_url', 'open_to_collaborate_default_text', 'attribution_incomplete_img_url', 'attribution_incomplete_svg_url', 'attribution_incomplete_default_text', 'created', 'updated',)

class ProjectOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('unique_id', 'providers_id', 'title', 'project_privacy', 'date_added', 'date_modified',)

# Notices only   
class ProjectSerializer(serializers.ModelSerializer):
    notice = NoticeSerializer(source="project_notice", many=True)
    institution_notice = InstitutionNoticeSerializer(source="project_institutional_notice", many=True)

    class Meta:
        model = Project
        fields = ('unique_id', 'providers_id', 'title', 'project_privacy', 'date_added', 'date_modified', 'notice', 'institution_notice', 'project_boundary_geojson')

# Labels only
class ProjectNoNoticeSerializer(serializers.ModelSerializer):
    bc_labels = BCLabelSerializer(many=True)
    tk_labels = TKLabelSerializer(many=True)

    class Meta:
        model = Project
        fields = ('unique_id', 'providers_id', 'title', 'project_privacy', 'date_added', 'date_modified', 'bc_labels', 'tk_labels', 'project_boundary_geojson')
