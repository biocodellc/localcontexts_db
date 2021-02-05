from django.urls import path
from . import views

urlpatterns = [
    path('connect-researcher/', views.connect_researcher, name="connect-researcher"),
    path('dashboard/<str:pk>', views.researcher_dashboard, name="researcher-dashboard"),
    path('dashboard/update/<str:pk>', views.update_researcher, name="researcher-update"),

    path('dashboard/notices/<str:pk>', views.researcher_notices, name="researcher-notices"),
    path('dashboard/notices/add/<str:pk>', views.add_notice, name="add-notice"),
    
    path('dashboard/relationships/<str:pk>', views.researcher_relationships, name="researcher-relationships"),
]