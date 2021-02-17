from rest_framework import serializers
from bclabels.models import *

class BCLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BCLabel
        fields = '__all__'