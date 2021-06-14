from rest_framework import serializers
from bclabels.models import BCLabel, BCNotice
from tklabels.models import TKLabel, TKNotice
from projects.models import Project, ProjectContributors, ProjectPerson
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
    class Meta:
        model = BCLabel
        fields = '__all__'

class TKLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TKLabel
        fields = '__all__'

class ProjectPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPerson
        fields = ('name',)

class ProjectContributorsSerializer(serializers.ModelSerializer):
    institutions = InstitutionSerializer(many=True)
    researchers = ResearcherSerializer(many=True)
    communities = CommunitySerializer(many=True)
    
    class Meta:
        model = ProjectContributors
        fields = ('institutions', 'researchers', 'communities',)

class ProjectSerializer(serializers.ModelSerializer):
    bclabels = BCLabelSerializer(many=True)
    tklabels = TKLabelSerializer(many=True)
    project_creator = UserSerializer()
    project_contributors = ProjectContributorsSerializer()
    additional_contributors = ProjectPersonSerializer(many=True)

    class Meta:
        model = Project
        fields = '__all__'

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
