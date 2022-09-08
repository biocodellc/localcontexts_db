from bclabels.models import BCLabel
from tklabels.models import TKLabel
from projects.models import Project
from rest_framework import viewsets, permissions
from .serializers import *

class BCLabelViewSet(viewsets.ModelViewSet):
    queryset = BCLabel.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = BCLabelSerializer

class TKLabelViewSet(viewsets.ModelViewSet):
    queryset = TKLabel.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = TKLabelSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = ProjectSerializer