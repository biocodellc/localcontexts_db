from api.base import serializers as base_serializers
from api.base.serializers import *

class LabelType(serializers.ModelSerializer):
    class Meta:
        model = TKLabel
        fields = ('TYPES')