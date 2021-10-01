from django.urls import path
from . import views

urlpatterns = [
    path('connect-institution/', views.connect_institution, name="connect-institution"),
    path('create-institution/', views.create_institution, name="create-institution"),
    path('create-institution/no-ror/', views.create_institution_noror, name="create-institution-noror"),
    path('confirm-institution/<str:institution_id>/', views.confirm_institution, name="confirm-institution"),

    path('institution/dashboard/update/<str:pk>/', views.update_institution, name="update-institution"),

    path('institution/notices/<str:pk>/', views.institution_notices, name="institution-notices"),

    path('institution/members/<str:pk>/', views.institution_members, name="institution-members"),
    path('institution/members/add/<str:pk>/', views.add_member, name="add-institution-member"),
    path('institution/members/remove/<str:pk>/<str:member_id>', views.remove_member, name="remove-institution-member"),

    path('institution/projects/<str:pk>/', views.institution_projects, name="institution-projects"),
    path('institution/projects/create-project/<str:pk>/', views.create_project, name="inst-create-project"),
    path('institution/projects/edit-project/<str:institution_id>/<str:project_uuid>', views.edit_project, name="inst-edit-project"),
    path('institution/projects/notify/<str:pk>/<str:proj_id>/', views.notify_others, name="institution-notify-others"),

    path('institution/restricted/<str:pk>/', views.restricted_view, name="institution-restricted"),

]