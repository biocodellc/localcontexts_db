from django.urls import path
from . import views

urlpatterns = [
    path('preparation-step/', views.preparation_step, name="prep-institution"),
    path('connect-institution/', views.connect_institution, name="connect-institution"),
    path('create-institution/', views.create_institution, name="create-institution"),
    path('create-institution/noROR', views.create_custom_institution, name="create-custom-institution"),
    path('confirm-institution/<str:institution_id>/', views.confirm_institution, name="confirm-institution"),

    # Public view
    path('view/<str:pk>/', views.public_institution_view, name="public-institution"),

    path('update/<str:pk>/', views.update_institution, name="update-institution"),

    path('notices/<str:pk>/', views.institution_notices, name="institution-notices"),
    path('notices/otc/delete/<str:pk>/<str:notice_id>/', views.delete_otc_notice, name="institution-delete-otc"),

    path('members/<str:pk>/', views.institution_members, name="institution-members"),
    path('members/requests/<str:pk>/', views.member_requests, name="institution-member-requests"),
    path('members/remove/<str:pk>/<str:member_id>', views.remove_member, name="remove-institution-member"),

    path('members/join-request/delete/<str:pk>/<str:join_id>', views.delete_join_request, name="institution-delete-join-request"),

    path('projects/<str:pk>/', views.institution_projects, name="institution-projects"),

    path('projects/create-project/<str:pk>/<uuid:source_proj_uuid>/<str:related>', views.create_project, name="inst-create-project"),
    path('projects/create-project/<str:pk>/<uuid:source_proj_uuid>/', views.create_project, name="inst-create-project"),
    path('projects/create-project/<str:pk>/', views.create_project, name="inst-create-project"),

    path('projects/edit-project/<str:pk>/<str:project_uuid>', views.edit_project, name="inst-edit-project"),
    path('projects/actions/<str:pk>/<uuid:project_uuid>/', views.project_actions, name="institution-project-actions"),
    path('projects/delete-project/<str:pk>/<str:project_uuid>', views.delete_project, name="inst-delete-project"),
    path('projects/archive-project/<str:pk>/<str:project_uuid>', views.archive_project, name="institution-archive-project"),

    path('projects/unlink/<str:pk>/<uuid:target_proj_uuid>/<uuid:proj_to_remove_uuid>', views.unlink_project, name="institution-unlink-project"),

    path('connections/<str:pk>/', views.connections, name="institution-connections"),
]