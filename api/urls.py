from django.urls import path, include, re_path
from .base.urls import urlpatterns as apiv1
from .versioned.v2.urls import urlpatterns as apiv2
from .views import redirect_view

urlpatterns = [
    path('', redirect_view),
    re_path(r'^v1/', include((apiv1, 'v1'), namespace='v1')),
    re_path(r'^v2/', include((apiv2, 'v2'), namespace='v2'))
]