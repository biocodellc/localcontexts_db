from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('verify', views.verify, name='verify'),
    path('activate/<uidb64>/<token>', views.ActivateAccountView.as_view(), name='activate'),
    path('create-profile', views.create_profile, name='create-profile'),
    path('connect-institution', views.connect_institution, name="connect-institution"),
    path('connect-community', views.connect_community, name="connect-community"),
]