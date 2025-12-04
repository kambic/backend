from django.contrib import admin
from django.urls import path

from django.urls import path, include
from rest_framework import routers

from dashboard.views import UserViewSet
from vod.api.v1.views import EdgeViewSet, ProviderViewSet, VueFinderViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"edgewares", EdgeViewSet)
router.register(r"providers", ProviderViewSet)
router.register(r"files", VueFinderViewSet, basename="files")

urlpatterns = [
    path("insight/", include("insight.urls")),
    path("api/", include(router.urls)),
    path("api/", include("vod.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("admin/", admin.site.urls),
]

from django.conf import settings

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns = [
        *urlpatterns,
    ] + debug_toolbar_urls()
