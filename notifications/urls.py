from django.urls import path
from . import views

urlpatterns = [
    path('read/<str:pk>/', views.read_notification, name="read"),
    path('delete/<str:pk>/', views.delete_notification, name="delete"),

    path('organization/read/<str:pk>', views.read_org_notification, name="org-read"),
]