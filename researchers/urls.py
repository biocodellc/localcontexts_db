from django.urls import path
from . import views

urlpatterns = [
    path('connect-researcher/', views.connect_researcher, name="connect-researcher"),
    path('researcher/dashboard/update/<str:pk>', views.update_researcher, name="researcher-update"),

    path('researcher/notices/<str:pk>', views.researcher_notices, name="researcher-notices"),
    path('researcher/activity/<str:pk>', views.researcher_activity, name="researcher-activity"),

    path('researcher/projects/<str:pk>', views.researcher_projects, name="researcher-projects"),
    path('researcher/projects/create-project/<str:pk>', views.create_project, name="researcher-create-project"),
    path('researcher/projects/notify/<str:pk>/<str:proj_id>/', views.notify_communities, name="researcher-notify-communities"),

    
    path('researcher/relationships/<str:pk>', views.researcher_relationships, name="researcher-relationships"),

]