from django.urls import path
from . import views

from rest_framework import routers
from .api import *

router = routers.DefaultRouter()
router.register('v1/bclabels', BCLabelViewSet, 'bclabels')
router.register('v1/tklabels', TKLabelViewSet, 'tklabels')
router.register('v1/projects', ProjectViewSet, 'projects')

urlpatterns = router.urls