from django.urls import path
from . import views

urlpatterns = [
    path('create-bclabel/', views.create_bclabel, name="create-bclabel"),
]