from django.urls import path
from . import views

from rest_framework import routers
from .api import *

# router = routers.DefaultRouter()
# router.register('v1/bclabels', BCLabelViewSet, 'bclabels')
# router.register('v1/tklabels', TKLabelViewSet, 'tklabels')
# router.register('v1/projects', ProjectViewSet, 'projects')

# urlpatterns = router.urls

urlpatterns = [
    path('v1/', views.apiOverview, name="api-overview"),

    path('v1/bclabels/', views.bclabels, name="api-bclabels"),
    path('v1/bclabel/<str:unique_id>/', views.bclabel_detail, name="api-bclabel-detail"),

    path('v1/tklabels/', views.tklabels, name="api-tklabels"),
    path('v1/tklabel/<str:unique_id>/', views.tklabel_detail, name="api-tklabel-detail"),

    path('v1/projects/', views.projects, name="api-projects"),
    path('v1/project/<str:unique_id>/', views.project_detail, name="api-project-detail"),
]