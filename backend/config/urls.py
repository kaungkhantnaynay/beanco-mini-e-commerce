from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from config import health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/live/", health.live, name="health-live"),
    path("health/ready/", health.ready, name="health-ready"),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="openapi-schema"),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="openapi-schema"),
        name="openapi-docs",
    ),
    path("api/v1/", include("apps.catalog.urls")),
    path("api/v1/", include("apps.communications.urls")),
]
