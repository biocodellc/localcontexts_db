from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:unique_id>/', views.view_project, name="view-project"),
    path('download/<uuid:unique_id>/', views.download_project, name="download-project-zip"),
    path('embed/<uuid:unique_id>/', views.embed_project, name="embed_project")
]