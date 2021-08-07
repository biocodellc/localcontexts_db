from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from bclabels.models import BCLabel, BCNotice
from tklabels.models import TKLabel, TKNotice
from projects.models import Project
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name',)

class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ('community_name',)

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ('institution_name',)

class ResearcherSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Researcher
        fields = ('user', 'orcid')

class BCLabelSerializer(serializers.ModelSerializer):
    community = CommunitySerializer()

    class Meta:
        model = BCLabel
        fields = ('name', 'label_type', 'default_text', 'img_url', 'community', 'created', 'updated')

class TKLabelSerializer(serializers.ModelSerializer):
    community = CommunitySerializer()

    class Meta:
        model = TKLabel
        fields = ('name', 'label_type', 'default_text', 'img_url', 'community', 'created', 'updated')

class ProjectSerializer(serializers.ModelSerializer):
    bclabels = BCLabelSerializer(many=True)
    tklabels = TKLabelSerializer(many=True)

    class Meta:
        model = Project
        fields = ('unique_id', 'title', 'bclabels', 'tklabels')

    # def get_notices_or_labels(self, obj):
    #     if self.bclabels.all().exists() or self.tklabels.all().exists():
    #         return self
    #     else:
    #         if self.project_bcnotice:
    #             return self.project_bcnotice
    #         elif self.project_tknotice:
    #             return self.project_tknotice
    #         else:
    #             return self

class BCNoticeSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    placed_by_institution = InstitutionSerializer()
    placed_by_researcher = ResearcherSerializer()
    communities = CommunitySerializer(many=True)

    class Meta:
        model = BCNotice
        fields = ('project', 'communities', 'placed_by_researcher', 'placed_by_institution', 'unique_id', 'created', 'updated',)

class TKNoticeSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    placed_by_institution = InstitutionSerializer()
    placed_by_researcher = ResearcherSerializer()
    communities = CommunitySerializer(many=True)

    class Meta:
        model = TKNotice
        fields = ('project', 'communities', 'placed_by_researcher', 'placed_by_institution', 'unique_id', 'created', 'updated',)
