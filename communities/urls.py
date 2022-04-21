from django.urls import path
from . import views

urlpatterns = [
    path('preparation-step/', views.preparation_step, name="prep-community"),
    path('connect-community/', views.connect_community, name="connect-community"),
    path('create-community/', views.create_community, name="create-community"),
    path('confirm-community/<str:community_id>/', views.confirm_community, name="confirm-community"),

    path('update/<str:pk>/', views.update_community, name="update-community"),

    path('members/<str:pk>/', views.community_members, name="members"),
    path('members/remove/<str:pk>/<str:member_id>', views.remove_member, name="remove-member"),
    
    path('labels/select/<str:pk>/', views.select_label, name="select-label"),
    path('labels/view/<str:pk>/<uuid:label_uuid>/', views.view_label, name="view-label"),

    path('labels/customize/<str:pk>/<str:label_type>', views.customize_label, name="customize-label"),
    path('labels/<str:pk>/<str:label_id>/', views.approve_label, name="approve-label"),
    path('labels/edit/<str:pk>/<str:label_id>/', views.edit_label, name="edit-label"),

    path('labels/apply-labels/<str:pk>/<str:project_uuid>', views.apply_labels, name="apply-labels"),

    path('projects/<str:pk>/', views.projects, name="community-projects"),
    path('projects/create-project/<str:pk>/', views.create_project, name="create-project"),
    path('projects/edit-project/<str:community_id>/<str:project_uuid>', views.edit_project, name="edit-project"),

    path('connections/<str:pk>/', views.connections, name="community-connections"),

    path('restricted/<str:pk>/', views.restricted_view, name="restricted"),
    
    path('labels-pdf/<str:pk>/', views.labels_pdf, name="labels-pdf"),
    path('labels-download/<str:pk>/', views.download_labels, name="download-labels"),

]