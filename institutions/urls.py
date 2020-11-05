from django.urls import path
from . import views

urlpatterns = [
    path('connect-institution', views.connect_institution, name="connect-institution"),
]