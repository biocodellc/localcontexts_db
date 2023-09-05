from django.urls import path
from . import views

urlpatterns = [
    path('preparation-step/', views.preparation_step, name="prep-community"),
    path('connect-community/', views.connect_community, name="connect-community"),
    path('create-community/', views.create_community, name="create-community"),
    path('confirm-community/<str:community_id>/', views.confirm_community, name="confirm-community"),

    # Public view
    path('view/<str:pk>/', views.public_community_view, name="public-community"),

    path('update/<str:pk>/', views.update_community, name="update-community"),

    path('members/<str:pk>/', views.community_members, name="members"),
    path('members/requests/<str:pk>/', views.member_requests, name="member-requests"),
    path('members/remove/<str:pk>/<str:member_id>', views.remove_member, name="remove-member"),

    path('members/join-request/delete/<str:pk>/<str:join_id>/', views.delete_join_request, name="delete-join-request"),
    
    path('labels/select/<str:pk>/', views.select_label, name="select-label"),
    path('labels/view/<str:pk>/<uuid:label_uuid>/', views.view_label, name="view-label"),

    path('labels/customize/<str:pk>/<str:label_code>/', views.customize_label, name="customize-label"),
    path('labels/<str:pk>/<str:label_id>/', views.approve_label, name="approve-label"),
    path('labels/edit/<str:pk>/<str:label_id>/', views.edit_label, name="edit-label"),

    path('labels/apply-labels/<str:pk>/<uuid:project_uuid>/', views.apply_labels, name="apply-labels"),

    path('projects/<str:pk>/', views.projects, name="community-projects"),

    path('projects/create-project/<str:pk>/<uuid:source_proj_uuid>/<str:related>', views.create_project, name="create-project"),
    path('projects/create-project/<str:pk>/<uuid:source_proj_uuid>/', views.create_project, name="create-project"),
    path('projects/create-project/<str:pk>/', views.create_project, name="create-project"),
    
    path('projects/edit-project/<str:pk>/<uuid:project_uuid>/', views.edit_project, name="edit-project"),
    path('projects/actions/<str:pk>/<uuid:project_uuid>/', views.project_actions, name="community-project-actions"),
    path('projects/delete-project/<str:pk>/<uuid:project_uuid>', views.delete_project, name="community-delete-project"),
    path('projects/archive-project/<str:pk>/<uuid:project_uuid>', views.archive_project, name="community-archive-project"),

    path('projects/unlink/<str:pk>/<uuid:target_proj_uuid>/<uuid:proj_to_remove_uuid>', views.unlink_project, name="community-unlink-project"),

    path('connections/<str:pk>/', views.connections, name="community-connections"),
    
    path('labels-pdf/<str:pk>/', views.labels_pdf, name="labels-pdf"),
    path('labels-download/<str:pk>/', views.download_labels, name="download-labels"),
]