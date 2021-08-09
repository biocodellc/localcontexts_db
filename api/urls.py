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

    path('v1/projects/', views.projects, name="api-projects"),
    path('v1/projects/<str:unique_id>/', views.project_detail, name="api-project-detail"),

    path('v1/projects/users/<str:username>/', views.projects_by_user, name="api-projects-user"),
    path('v1/projects/institutions/<str:institution_id>/', views.projects_by_institution, name="api-projects-institution"),
    path('v1/projects/researchers/<str:researcher_id>/', views.projects_by_researcher, name="api-projects-researcher"),
]