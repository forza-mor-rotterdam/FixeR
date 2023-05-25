from apps.main.views import (
    config,
    filter,
    http_404,
    http_500,
    incident_detail,
    incident_list,
    incident_list_item,
    incident_list_page,
    incident_modal_handle,
    incident_mutation_lines,
    meldingen_bestand,
    root,
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
    path("v1/", include((router.urls, "app"), namespace="v1")),
    path("admin/", admin.site.urls),
    path("", root, name="root"),
    path(
        "incident/",
        incident_list_page,
        name="incident_index",
    ),
    path("incident/<int:id>/", incident_detail, name="incident_detail"),
    path(
        "incident/<int:id>/mutation-lines/",
        incident_mutation_lines,
        name="mutation_lines",
    ),
    path("config/", config, name="config"),
    path("health/", include("health_check.urls")),
    # START partials
    path("part/pageheader-form/", ui_settings_handler, name="pageheader_form_part"),
    path("part/filter/", filter, name="filter_part"),
    path("part/incident-list/", incident_list, name="incident_list_part"),
    path(
        "part/incident-list-item/<int:id>/",
        incident_list_item,
        name="incident_list_item_part",
    ),
    path(
        "part/incident-modal-handle/<int:id>/",
        incident_modal_handle,
        name="incident_modal_handle_part",
    ),
    path(
        "part/incident-modal-handle/<int:id>/<str:handled_type>/",
        incident_modal_handle,
        name="incident_modal_handled_type_part",
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
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
