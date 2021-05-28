from rest_framework import serializers
from bclabels.models import BCLabel, BCNotice
from tklabels.models import TKLabel, TKNotice
from projects.models import Project

class BCLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BCLabel
        fields = '__all__'

class TKLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TKLabel
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    bclabels = BCLabelSerializer(many=True)
    tklabels = TKLabelSerializer(many=True)

    class Meta:
        model = Project
        fields = '__all__'

class BCNoticeSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()

    class Meta:
        model = BCNotice
        fields = '__all__'

class TKNoticeSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()

    class Meta:
        model = TKNotice
        fields = '__all__'