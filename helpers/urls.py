from django.urls import path
from . import views

urlpatterns = [
    path('download/open-to-collaborate-notice/<int:perm>/', views.download_open_collaborate_notice, name="download-open-to-collaborate-notice"),
    path('download/collections-care-notices/<int:perm>/', views.download_collections_care_notices, name="download-collections-care-notices"),
    path('invite/delete/<str:pk>/', views.delete_member_invite, name="delete-member-invite"),
    path('download/community/support-letter/', views.download_community_support_letter, name="download-community-support-letter"),
    path('download/institution/support-letter/', views.download_institution_support_letter, name="download-institution-support-letter"),

]