from django.urls import path
from . import views

urlpatterns = [
    path('<str:unique_id>/', views.view_project, name="view-project"),
    path('download/<str:unique_id>/', views.download_project_zip, name="download-project-zip"),
]