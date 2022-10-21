from api.base import serializers as base_serializers
from api.base.serializers import *

from .models import KeyList
from rest_framework_api_key.models import BaseAPIKeyManager

class APIKeySerializer(serializers.Serializer):
    class Meta:
        model = KeyList
        fields = ('key', 'id', 'hashed_key')