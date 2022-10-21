from django.urls import path, re_path
from .views import *

multisearch = MultiProjectListDetail.as_view({
    'get':'multisearch'
})

urlpatterns = [
    re_path(r'^$', apiOverview, name="api-overview"),
    path('notices/open_to_collaborate', openToCollaborateNotice, name="api-open-to-collaborate"),

    path('projects/', ProjectList.as_view(), name="api-projects"),
    path('projects/<unique_id>/', ProjectDetail.as_view(), name="api-project-detail"),
    path('projects/external/<str:providers_id>/', project_detail_providers, name="api-project-detail-providers"),

    path('projects/users/<str:pk>/', projects_by_user, name="api-projects-user"),
    path('projects/institutions/<str:institution_id>/', projects_by_institution, name="api-projects-institution"),
    path('projects/researchers/<str:researcher_id>/', projects_by_researcher, name="api-projects-researcher"),

    path('projects/multi/<unique_id>/', multisearch, name="api-projects-multi")
]