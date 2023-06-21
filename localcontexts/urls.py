"""localcontexts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from helpers.views import restricted_view

admin.site.site_header = 'Local Contexts Hub administration'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('communities/', include('communities.urls')),
    path('institutions/', include('institutions.urls')),
    path('researchers/', include('researchers.urls')),
    path('projects/', include('projects.urls')),    
    path('helpers/', include('helpers.urls')),
    path('api/', include('api.urls')),
    path('restricted/403/', restricted_view, name="restricted"),

    path('notifications/', include('notifications.urls')),

    re_path(r'^maintenance-mode/', include('maintenance_mode.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # import debug_toolbar
    urlpatterns += path('__debug__/', include('debug_toolbar.urls')),
