from django.urls import path
from . import views

urlpatterns = [
    path('download/open-to-collaborate-notice/', views.download_open_collaborate_notice, name="download-open-to-collaborate-notice"),
    path('restricted/', views.restricted_view, name="restricted"),
    path('invite/delete/<str:pk>/', views.delete_member_invite, name="delete-member-invite"),
]