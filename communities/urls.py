from django.urls import path
from . import views

urlpatterns = [
    path('connect-community/', views.connect_community, name="connect-community"),
    path('create-community/', views.create_community, name="create-community"),
    path('community-registry/', views.community_registry, name="community-registry"),
    path('community/<str:pk>/', views.community_dashboard, name="community-dashboard"),
    path('community/members/<str:pk>/', views.community_members, name="members"),
    path('community/members/add-members/<str:pk>/', views.add_members, name="add-members"),
]