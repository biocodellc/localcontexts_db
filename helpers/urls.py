from django.urls import path
from . import views

urlpatterns = [
    path('download/open-to-collaborate-notice/<int:perm>/', views.download_open_collaborate_notice, name="download-open-to-collaborate-notice"),
    path('invite/delete/<str:pk>/', views.delete_member_invite, name="delete-member-invite"),
]