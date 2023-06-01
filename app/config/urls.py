from apps.main.views import (
    actieve_taken,
    config,
    filter,
    http_404,
    http_500,
    incident_list_item,
    incident_modal_handle,
    incident_mutation_lines,
    meldingen_bestand,
    root,
    taak_detail,
    taken_overzicht,
    ui_settings_handler,
)
from apps.taken.viewsets import TaaktypeViewSet, TaakViewSet
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"taak", TaakViewSet, basename="taak")
router.register(r"taaktype", TaaktypeViewSet, basename="taaktype")

urlpatterns = [
    path("api/v1/", include((router.urls, "app"), namespace="v1")),
    path("admin/", admin.site.urls),
    path("", root, name="root"),
    path(
        "taken/",
        taken_overzicht,
        name="incident_index",
    ),
    path("taak/<int:id>/", taak_detail, name="taak_detail"),
    path(
        "taak/<int:id>/mutation-lines/",
        incident_mutation_lines,
        name="mutation_lines",
    ),
    path("config/", config, name="config"),
    path("health/", include("health_check.urls")),
    # START partials
    path("part/pageheader-form/", ui_settings_handler, name="pageheader_form_part"),
    path("part/filter/", filter, name="filter_part"),
    path("part/actieve-taken/", actieve_taken, name="actieve_taken_part"),
    path(
        "part/taak-lijst-item/<int:id>/",
        incident_list_item,
        name="incident_list_item_part",
    ),
    path(
        "part/taak-modal-handle/<int:id>/",
        incident_modal_handle,
        name="incident_modal_handle_part",
    ),
    path(
        "part/taak-modal-handle/<int:id>/<str:handled_type>/",
        incident_modal_handle,
        name="incident_modal_handled_type_part",
    ),
    path("api/schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
    # Optional UI:
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    re_path(r"media/", meldingen_bestand, name="meldingen_bestand"),
]

if settings.DEBUG:
    urlpatterns += [
        path("404/", http_404, name="404"),
        path("500/", http_500, name="500"),
    ]
