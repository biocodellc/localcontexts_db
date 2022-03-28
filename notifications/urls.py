from django.urls import path
from . import views

urlpatterns = [
    path('show/<str:pk>/', views.show_notification, name="show"),
    path('read/<str:pk>/', views.read_notification, name="read"),
    path('delete/<str:pk>/', views.delete_notification, name="delete"),

    path('organization/read/<str:pk>', views.read_org_notification, name="org-read"),
]