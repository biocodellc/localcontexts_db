from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),

    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),

    path('activate/<uidb64>/<token>', views.ActivateAccountView.as_view(), name='activate'),
    path('verify/', views.verify, name='verify'),

    path('invite/', views.invite_user, name='invite'),
    path('member-invites/', views.member_invitations, name='member-invitations'),
    path('member-invites/delete/<str:pk>/', views.delete_member_invitation, name='delete-member-invitation'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('onboarding/on', views.onboarding_on, name='onboarding-on'),
    path('create-profile/', views.create_profile, name='create-profile'),

    path('update-profile/', views.update_profile, name='update-profile'),
    path('manage/', views.manage_organizations, name='manage-orgs'),
    path('change-password/', views.change_password, name='change-password'),
    path('deactivate/', views.deactivate_user, name='deactivate-user'),

    path('select-account/', views.select_account, name='select-account'),
    
    # path('registry/communities/', views.registry_communities, name='community-registry'),
    # path('registry/institutions/', views.registry_institutions, name='institution-registry'),
    # path('registry/researchers/', views.registry_researchers, name='researcher-registry'),
    path('registry/', views.registry_updated, name='registry'),
    path('registry/<str:filtertype>/', views.registry_updated, name='registry'),
    path('counter/', views.hub_counter, name='hub-counter'),
    path('newsletter/subscribe/', views.newsletter_subscription, name='newsletter-subscription'),
    path('newsletter/preferences/<emailb64>/', views.newsletter_unsubscription, name='newsletter-unsubscription'),


    path('reset-password/', auth_views.PasswordResetView.as_view(template_name="accounts/password-reset.html"), name="reset_password"),
    path('reset-password-sent/', auth_views.PasswordResetDoneView.as_view(template_name="accounts/password-reset-sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password-reset-confirm.html"), name="password_reset_confirm"),
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password-reset-done.html"), name="password_reset_complete"),

    path('apikey/', views.api_keys, name='api-key'),

]