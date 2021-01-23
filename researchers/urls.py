from django.urls import path
from . import views

urlpatterns = [
    path('connect-researcher/', views.connect_researcher, name="connect-researcher"),
    path('dashboard/<str:pk>', views.researcher_dashboard, name="researcher-dashboard"),
    path('dashboard/notices/<str:pk>', views.researcher_notices, name="researcher-notices"),
    path('dashboard/relationships/<str:pk>', views.researcher_relationships, name="researcher-relationships"),
]