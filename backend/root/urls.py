"""srachat URL Configuration

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
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from . import settings
from .views import HealthCheck, index

SCHEMA_NAME = "api-schema"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('srachat.urls')),  # route to api calls
    # Use the `get_schema_view()` helper to add a `SchemaView` to project URLs.
    #   * `title` and `description` parameters are passed to `SchemaGenerator`.
    #   * Provide view name for use with `reverse()`.
    path('schema-api/', get_schema_view(
        title="Srachat API Scheme",
        description="API for all things … and other",
        version="0.0.0"
    ), name=SCHEMA_NAME),
    # Route TemplateView to serve Swagger UI template.
    #   * Provide `extra_context` with view name of `SchemaView`.
    path('swagger/', TemplateView.as_view(
        template_name='swagger.html',
        extra_context={'schema_url': SCHEMA_NAME}
    ), name='swagger'),

    # Health check
    path('health/', HealthCheck.as_view()),


    # Front end view as an entry point
    path('', index, name="index"),

]

# For serving media files in development mode.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
