from django.urls import path
from . import views

urlpatterns = [
    path('show/<str:pk>/', views.show_notification, name="show"),
    path('delete/<str:pk>/', views.delete_notification, name="delete"),
]