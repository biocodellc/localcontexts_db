from django.urls import path
from . import views

urlpatterns = [
    path('connect-community', views.connect_community, name="connect-community"),
]