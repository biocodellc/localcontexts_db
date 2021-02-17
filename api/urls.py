from django.urls import path
from . import views

from rest_framework import routers
from .api import BCLabelViewSet

router = routers.DefaultRouter()
router.register('v1/bclabels', BCLabelViewSet, 'bclabels')

urlpatterns = router.urls