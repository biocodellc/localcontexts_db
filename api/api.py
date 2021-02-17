from bclabels.models import *
from rest_framework import viewsets, permissions
from .serializers import BCLabelSerializer

class BCLabelViewSet(viewsets.ModelViewSet):
    queryset = BCLabel.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = BCLabelSerializer