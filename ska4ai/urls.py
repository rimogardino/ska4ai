"""
URL configuration for ska4ai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.urls import include, path
from django.conf import settings
from django.urls import re_path
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('set_language/', set_language, name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path("", include("home.urls")),
    path("events/", include("events.urls")),
    path("challenges/", include("challenges.urls")),
    path("submissions/", include("submissions.urls")),
    path("userinteraction/", include("userinteraction.urls")),
    
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path('accounts/', include('allauth.urls')),
)

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]