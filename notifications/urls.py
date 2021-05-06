from django.urls import path
from . import views

urlpatterns = [
    path('show/<str:pk>/', views.show_notification, name="show"),
    path('read/<str:pk>/', views.read_notification, name="read"),
    path('delete/<str:pk>/', views.delete_notification, name="delete"),

    path('show/<str:cid>/<str:pk>', views.show_notification_community, name="comm-show"),
    path('community/read/<str:cid>/<str:pk>', views.read_notification_community, name="comm-read"),
    path('institution/read/<str:iid>/<str:pk>', views.read_institution_notification, name="inst-read"),
    path('researcher/read/<str:rid>/<str:pk>', views.read_researcher_notification, name="researcher-read"),

]