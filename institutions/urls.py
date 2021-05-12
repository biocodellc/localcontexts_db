from django.urls import path
from . import views

urlpatterns = [
    path('connect-institution/', views.connect_institution, name="connect-institution"),
    path('create-institution/', views.create_institution, name="create-institution"),
    path('institution-registry/', views.institution_registry, name="institution-registry"),

    path('institution/dashboard/update/<str:pk>/', views.update_institution, name="update-institution"),

    path('institution/notices/<str:pk>/', views.institution_notices, name="institution-notices"),
    path('institution/activity/<str:pk>/', views.institution_activity, name="institution-activity"),

    path('institution/members/<str:pk>/', views.institution_members, name="institution-members"),
    path('institution/members/add/<str:pk>/', views.add_member, name="add-institution-member"),

    path('institution/projects/<str:pk>/', views.institution_projects, name="institution-projects"),
    path('institution/projects/create-project/<str:pk>/', views.create_project, name="inst-create-project"),
    path('institution/projects/notify/<str:pk>/<str:proj_id>/', views.notify_communities, name="notify-communities"),

    path('institution/restricted/<str:pk>/', views.restricted_view, name="institution-restricted"),

]