from django.urls import path
from . import views

urlpatterns = [
    path('download/open-to-collaborate-notice/researcher/<int:perm>/<int:researcher_id>/', views.download_open_collaborate_notice, name="download-open-to-collaborate-notice-researcher"),
    path('download/open-to-collaborate-notice/institution/<int:perm>/<int:institution_id>/', views.download_open_collaborate_notice, name="download-open-to-collaborate-notice-institution"),
    path('download/collections-care-notices/<str:institution_id>/<int:perm>/', views.download_collections_care_notices, name="download-collections-care-notices"),
    path('invite/delete/<str:pk>/', views.delete_member_invite, name="delete-member-invite"),
    path('download/community/support-letter/', views.download_community_support_letter, name="download-community-support-letter"),
    path('download/institution/support-letter/', views.download_institution_support_letter, name="download-institution-support-letter"),

]