from django.urls import path
from . import views

urlpatterns = [
    path('view-project/<str:unique_id>/', views.view_project, name="view-project"),
]