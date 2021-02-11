from django.urls import path
from . import views

urlpatterns = [
    path('connect-community/', views.connect_community, name="connect-community"),
    path('create-community/', views.create_community, name="create-community"),
    path('community-registry/', views.community_registry, name="community-registry"),

    path('community/<str:pk>/', views.community_dashboard, name="community-dashboard"),
    path('community/update/<str:pk>/', views.update_community, name="update-community"),

    path('community/members/<str:pk>/', views.community_members, name="members"),
    path('community/members/add/<str:pk>/', views.add_member, name="add-member"),
    
    path('community/requests/<str:pk>/', views.community_requests, name="community-requests"),

    path('community/labels/<str:pk>/', views.community_labels, name="community-labels"),
    path('community/labels/create/<str:pk>/', views.create_label, name="create-label"),
    path('community/labels/add/<str:pk>/<str:notice_id>', views.community_add_labels, name="community-add-labels"),

    path('community/labels/create-project/<str:pk>/', views.create_project, name="create-project"),

    path('community/relationships/<str:pk>/', views.community_relationships, name="community-relationships"),

    path('community/restricted/<str:pk>/', views.restricted_view, name="restricted"),
]