from django.urls import path
from . import views

urlpatterns = [
    path('preparation-step/', views.preparation_step, name="prep-institution"),
    path('connect-institution/', views.connect_institution, name="connect-institution"),
    path('create-institution/', views.create_institution, name="create-institution"),
    path('confirm-institution/<str:institution_id>/', views.confirm_institution, name="confirm-institution"),

    path('update/<str:pk>/', views.update_institution, name="update-institution"),

    path('notices/<str:pk>/', views.institution_notices, name="institution-notices"),

    path('members/<str:pk>/', views.institution_members, name="institution-members"),
    path('members/requests/<str:pk>/', views.member_requests, name="institution-member-requests"),
    path('members/remove/<str:pk>/<str:member_id>', views.remove_member, name="remove-institution-member"),

    path('members/join-request/delete/<str:pk>/<str:join_id>', views.delete_join_request, name="institution-delete-join-request"),

    path('projects/<str:pk>/', views.institution_projects, name="institution-projects"),
    path('projects/create-project/<str:pk>/', views.create_project, name="inst-create-project"),
    path('projects/edit-project/<str:institution_id>/<str:project_uuid>', views.edit_project, name="inst-edit-project"),
    path('projects/notify/<str:pk>/<str:proj_id>/', views.notify_others, name="institution-notify-others"),

    path('connections/<str:pk>/', views.connections, name="institution-connections"),

    path('restricted/<str:pk>/', views.restricted_view, name="institution-restricted"),

]