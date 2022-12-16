from django.urls import path
from . import views

urlpatterns = [
    path('preparation-step/', views.preparation_step, name="prep-institution"),
    path('connect-institution/', views.connect_institution, name="connect-institution"),
    path('create-institution/', views.create_institution, name="create-institution"),
    path('confirm-institution/<str:institution_id>/', views.confirm_institution, name="confirm-institution"),

    # Public view
    path('view/<str:pk>/', views.public_institution_view, name="public-institution"),

    path('update/<str:pk>/', views.update_institution, name="update-institution"),

    path('notices/<str:pk>/', views.institution_notices, name="institution-notices"),
    path('notices/otc/delete/<str:institution_id>/<str:notice_id>/', views.delete_otc_notice, name="institution-delete-otc"),

    path('members/<str:pk>/', views.institution_members, name="institution-members"),
    path('members/requests/<str:pk>/', views.member_requests, name="institution-member-requests"),
    path('members/remove/<str:pk>/<str:member_id>', views.remove_member, name="remove-institution-member"),

    path('members/join-request/delete/<str:pk>/<str:join_id>', views.delete_join_request, name="institution-delete-join-request"),

    path('projects/<str:pk>/', views.institution_projects, name="institution-projects"),
    path('projects-labels/<str:pk>/', views.projects_with_labels, name="institution-projects-labels"),
    path('projects-notices/<str:pk>/', views.projects_with_notices, name="institution-projects-notices"),
    path('projects-created/<str:pk>/', views.projects_creator, name="institution-projects-creator"),
    path('projects-contributing/<str:pk>/', views.projects_contributor, name="institution-projects-contributor"),


    path('projects/create-project/<str:pk>/', views.create_project, name="inst-create-project"),
    path('projects/edit-project/<str:institution_id>/<str:project_uuid>', views.edit_project, name="inst-edit-project"),
    path('projects/actions/<str:pk>/<uuid:project_uuid>/', views.project_actions, name="institution-project-actions"),
    path('projects/delete-project/<str:institution_id>/<str:project_uuid>', views.delete_project, name="inst-delete-project"),

    path('connections/<str:pk>/', views.connections, name="institution-connections"),
]