from django.urls import path
from . import views

urlpatterns = [
    path('show/<str:pk>/', views.show_notification, name="show"),
    path('read/<str:pk>/', views.read_notification, name="read"),
    path('delete/<str:pk>/', views.delete_notification, name="delete"),

    path('community/show/<str:pk>/', views.show_notification_community, name="show-comm"),
    path('community/delete/<str:pk>/', views.delete_notification_community, name="delete-comm"),
]