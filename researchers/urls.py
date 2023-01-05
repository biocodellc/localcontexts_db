from django.urls import path
from . import views

urlpatterns = [
    path('connect-researcher/', views.connect_researcher, name="connect-researcher"),
    path('connect-orcid/', views.connect_orcid, name="connect-orcid"),
    path('disconnect-orcid/', views.disconnect_orcid, name="disconnect-orcid"),
    
    # Public view
    path('view/<str:pk>/', views.public_researcher_view, name="public-researcher"),

    path('update/<str:pk>', views.update_researcher, name="update-researcher"),

    path('notices/<str:pk>', views.researcher_notices, name="researcher-notices"),
    path('notices/otc/delete/<str:researcher_id>/<str:notice_id>/', views.delete_otc_notice, name="researcher-delete-otc"),

    path('projects/<str:pk>', views.researcher_projects, name="researcher-projects"),
    path('projects-notices/<str:pk>/', views.projects_with_notices, name="researcher-projects-notices"),
    path('projects-labels/<str:pk>/', views.projects_with_labels, name="researcher-projects-labels"),

    path('projects-created/<str:pk>/', views.projects_creator, name="researcher-projects-creator"),
    path('projects-contributing/<str:pk>/', views.projects_contributor, name="researcher-projects-contributor"),
    path('projects-archived/<str:pk>/', views.projects_archived, name="researcher-projects-archived"),

    path('projects/create-project/<str:pk>', views.create_project, name="researcher-create-project"),
    path('projects/edit-project/<str:researcher_id>/<str:project_uuid>/', views.edit_project, name="researcher-edit-project"),
    path('projects/actions/<str:pk>/<uuid:project_uuid>/', views.project_actions, name="researcher-project-actions"),
    path('projects/delete-project/<str:researcher_id>/<str:project_uuid>/', views.delete_project, name="researcher-delete-project"),
    path('projects/archive-project/<str:researcher_id>/<str:project_uuid>', views.archive_project, name="researcher-archive-project"),

    path('connections/<str:pk>/', views.connections, name="researcher-connections"),
]