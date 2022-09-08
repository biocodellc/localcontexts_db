from django.urls import path, include, re_path
from .base.urls import urlpatterns as apiv1
from .versioned.v2.urls import urlpatterns as apiv2


urlpatterns = [
    re_path(r'^v1/', include((apiv1, 'v1'), namespace='v1')),
    re_path(r'^v2/', include((apiv2, 'v2'), namespace='v2'))
]