from django.urls import path
from .views import *
from .api import *


urlpatterns = [
    path('v1/', apiOverview, name="api-overview"),

    path('v1/projects/', ProjectList.as_view(), name="api-projects"),
    path('v1/projects/<uuid:unique_id>/', project_detail, name="api-project-detail"),
    path('v1/projects/external/<str:providers_id>/', project_detail_providers, name="api-project-detail-providers"),

    path('v1/projects/users/<str:username>/', projects_by_user, name="api-projects-user"),
    path('v1/projects/institutions/<str:institution_id>/', projects_by_institution, name="api-projects-institution"),
    path('v1/projects/researchers/<str:researcher_id>/', projects_by_researcher, name="api-projects-researcher"),
]