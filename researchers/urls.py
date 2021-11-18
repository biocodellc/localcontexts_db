from django.urls import path
from . import views

urlpatterns = [
    path('connect-researcher/', views.connect_researcher, name="connect-researcher"),
    path('researcher/dashboard/update/<str:pk>', views.update_researcher, name="researcher-update"),

    path('researcher/notices/<str:pk>', views.researcher_notices, name="researcher-notices"),

    path('researcher/projects/<str:pk>', views.researcher_projects, name="researcher-projects"),
    path('researcher/projects/create-project/<str:pk>', views.create_project, name="researcher-create-project"),
    path('researcher/projects/edit-project/<str:researcher_id>/<str:project_uuid>', views.edit_project, name="researcher-edit-project"),
    path('researcher/projects/notify/<str:pk>/<str:proj_id>/', views.notify_others, name="researcher-notify-others"),

    path('researcher/connections/<str:pk>/', views.connections, name="researcher-connections"),

    path('researcher/restricted/<str:pk>', views.restricted_view, name="researcher-restricted"),

]