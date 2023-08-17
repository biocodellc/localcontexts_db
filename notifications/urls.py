from django.urls import path
from . import views

urlpatterns = [
    path('read/<str:pk>/', views.read_notification, name="read"),
    path('user-notification/delete/<str:pk>/', views.delete_user_notification, name="delete-user-notification"),

    path('organization/read/<str:pk>', views.read_org_notification, name="org-read"),
]