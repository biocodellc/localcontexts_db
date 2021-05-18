from rest_framework import serializers
from bclabels.models import BCLabel
from tklabels.models import TKLabel
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
    class Meta:
        model = Project
        fields = '__all__'