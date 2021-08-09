from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from bclabels.models import BCLabel, BCNotice
from tklabels.models import TKLabel, TKNotice
from projects.models import Project
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from django.contrib.auth.models import User

class ResearcherSerializer(serializers.ModelSerializer):
    user = SerializerMethodField()

    class Meta:
        model = Researcher
        fields = ('user', 'orcid')

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

class BCNoticeSerializer(serializers.ModelSerializer):
    placed_by_institution = SerializerMethodField()
    placed_by_researcher = ResearcherSerializer()

    class Meta:
        model = BCNotice
        fields = ('unique_id', 'img_url', 'placed_by_researcher', 'placed_by_institution', 'created', 'updated',)

    def get_placed_by_institution(self, obj):
        return str(obj.placed_by_institution)
    
class TKNoticeSerializer(serializers.ModelSerializer):
    placed_by_institution = SerializerMethodField()
    placed_by_researcher = ResearcherSerializer()

    class Meta:
        model = TKNotice
        fields = ('unique_id', 'img_url', 'placed_by_researcher', 'placed_by_institution', 'created', 'updated',)
    
    def get_placed_by_institution(self, obj):
        return str(obj.placed_by_institution)

class ProjectSerializer(serializers.ModelSerializer):
    bclabels = BCLabelSerializer(many=True)
    tklabels = TKLabelSerializer(many=True)
    bcnotice = BCNoticeSerializer(source="project_bcnotice", many=True)
    tknotice = BCNoticeSerializer(source="project_tknotice", many=True)

    class Meta:
        model = Project
        fields = ('unique_id', 'title', 'bcnotice', 'tknotice', 'bclabels', 'tklabels')
