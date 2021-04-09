from django.urls import path
from . import views

urlpatterns = [
    path('connect-institution/', views.connect_institution, name="connect-institution"),
    path('create-institution/', views.create_institution, name="create-institution"),
    path('institution-registry/', views.institution_registry, name="institution-registry"),

    path('institution/dashboard/<str:pk>/', views.institution_dashboard, name="institution-dashboard"),
    path('institution/dashboard/update/<str:pk>/', views.update_institution, name="update-institution"),

    path('institution/notices/<str:pk>/', views.institution_notices, name="institution-notices"),
    path('institution/requests/<str:pk>/', views.institution_requests, name="institution-requests"),

    path('institution/projects/<str:pk>/', views.institution_projects, name="institution-projects"),
    path('institution/projects/create-project/<str:pk>/', views.create_project, name="inst-create-project"),
    path('institution/projects/notify/<str:pk>/<str:proj_id>/', views.notify_communities, name="notify-communities"),
]