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

    path('v1/bcnotices/', views.bcnotices, name="api-bcnotices"),
    path('v1/bcnotices/<str:unique_id>/', views.bcnotice_detail, name="api-bcnotice-detail"),

    path('v1/tknotices/', views.tknotices, name="api-tknotices"),
    path('v1/tknotices/<str:unique_id>/', views.tknotice_detail, name="api-tknotice-detail"),

    path('v1/projects/', views.projects, name="api-projects"),
    path('v1/projects/<str:unique_id>/', views.project_detail, name="api-project-detail"),
]