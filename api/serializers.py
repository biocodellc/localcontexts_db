from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from helpers.models import Notice
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

class BCLabelSerializer(serializers.ModelSerializer):
    community = SerializerMethodField()

    class Meta:
        model = BCLabel
        fields = ('name', 'label_type', 'default_text', 'img_url', 'community', 'created', 'updated')
    
    def get_community(self, obj):
        return str(obj.community.community_name)

class TKLabelSerializer(serializers.ModelSerializer):
    community = SerializerMethodField()

    class Meta:
        model = TKLabel
        fields = ('name', 'label_type', 'default_text', 'img_url', 'community', 'created', 'updated')

    def get_community(self, obj):
        return str(obj.community.community_name)

class NoticeSerializer(serializers.ModelSerializer):
    placed_by_institution = InstitutionSerializer()
    placed_by_researcher = ResearcherSerializer()

    class Meta:
        model = Notice
        fields = ('notice_type', 'bc_img_url', 'bc_default_text', 'tk_img_url', 'tk_default_text', 'placed_by_researcher', 'placed_by_institution', 'created', 'updated',)

class ProjectOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('unique_id', 'title',)
    
class ProjectSerializer(serializers.ModelSerializer):
    bc_labels = BCLabelSerializer(many=True)
    tk_labels = TKLabelSerializer(many=True)
    notice = NoticeSerializer(source="project_notice", many=True)

    class Meta:
        model = Project
        fields = ('unique_id', 'title', 'notice', 'bc_labels', 'tk_labels')
