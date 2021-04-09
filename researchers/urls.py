from django.urls import path
from . import views

urlpatterns = [
    path('connect-researcher/', views.connect_researcher, name="connect-researcher"),
    path('researcher/dashboard/<str:pk>', views.researcher_dashboard, name="researcher-dashboard"),
    path('researcher/dashboard/update/<str:pk>', views.update_researcher, name="researcher-update"),

    path('researcher/projects/<str:pk>', views.researcher_notices, name="researcher-notices"),
    path('researcher/projects/create-project/<str:pk>', views.add_notice, name="add-notice"),
    
    path('researcher/relationships/<str:pk>', views.researcher_relationships, name="researcher-relationships"),
]