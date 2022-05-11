from django.urls import path
from . import views

urlpatterns = [
    path('connect-researcher/', views.connect_researcher, name="connect-researcher"),
    path('connect-orcid/', views.connect_orcid, name="connect-orcid"),
    path('disconnect-orcid/', views.disconnect_orcid, name="disconnect-orcid"),
    
    path('update/<str:pk>', views.update_researcher, name="researcher-update"),

    path('notices/<str:pk>', views.researcher_notices, name="researcher-notices"),

    path('projects/<str:pk>', views.researcher_projects, name="researcher-projects"),
    path('projects/create-project/<str:pk>', views.create_project, name="researcher-create-project"),
    path('projects/edit-project/<str:researcher_id>/<str:project_uuid>', views.edit_project, name="researcher-edit-project"),
    path('projects/notify/<str:pk>/<str:proj_id>/', views.notify_others, name="researcher-notify-others"),

    path('connections/<str:pk>/', views.connections, name="researcher-connections"),
]