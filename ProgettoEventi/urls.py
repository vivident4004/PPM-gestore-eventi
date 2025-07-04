"""
URL configuration for ProgettoEventi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Add this for language selection
]

# Add all other URL patterns that should be translated
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    # Add a redirect for admin without trailing slash
    path('admin', RedirectView.as_view(url='admin/', permanent=True)),
    path('accounts/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),
    path('events/', include('GestoreEventi.urls')),
    path('', RedirectView.as_view(url='events/', permanent=True)),
    prefix_default_language=True,  # Include language code for all languages
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
