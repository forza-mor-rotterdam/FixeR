from apps.beheer.views import (
    GebruikerAanmakenView,
    GebruikerAanpassenView,
    GebruikerLijstView,
    beheer,
)
from apps.main.views import (
    account,
    actieve_taken,
    afgeronde_taken,
    config,
    filter,
    http_404,
    http_500,
    incident_list_item,
    incident_modal_handle,
    meldingen_bestand,
    root,
    taak_detail,
    taken_afgerond_overzicht,
    taken_overzicht,
    ui_settings_handler,
)
from apps.taken.viewsets import TaaktypeViewSet, TaakViewSet
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"taak", TaakViewSet, basename="taak")
router.register(r"taaktype", TaaktypeViewSet, basename="taaktype")

urlpatterns = [
    path("", root, name="root"),
    path("account/", account, name="account"),
    path("api/v1/", include((router.urls, "app"), namespace="v1")),
    path("api-token-auth/", views.obtain_auth_token),
    path("admin/", admin.site.urls),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path(
        "taken/",
        taken_overzicht,
        name="incident_index",
    ),
    path(
        "taken-afgerond/",
        taken_afgerond_overzicht,
        name="taken_afgerond_overzicht",
    ),
    path("taak/<int:id>/", taak_detail, name="taak_detail"),
    path("config/", config, name="config"),
    path("health/", include("health_check.urls")),
    # START partials
    path("part/pageheader-form/", ui_settings_handler, name="pageheader_form_part"),
    path("part/filter/", filter, name="filter_part"),
    path("part/filter/<str:openstaand>/", filter, name="filter_part"),
    path("part/actieve-taken/", actieve_taken, name="actieve_taken_part"),
    path("part/afgeronde-taken/", afgeronde_taken, name="afgeronde_taken_part"),
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
    path("beheer/", beheer, name="beheer"),
    path("beheer/gebruiker/", GebruikerLijstView.as_view(), name="gebruiker_lijst"),
    path(
        "beheer/gebruiker/aanmaken/",
        GebruikerAanmakenView.as_view(),
        name="gebruiker_aanmaken",
    ),
    path(
        "beheer/gebruiker/<int:pk>/aanpassen/",
        GebruikerAanpassenView.as_view(),
        name="gebruiker_aanpassen",
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

if settings.OIDC_ENABLED:
    urlpatterns += [
        path(
            "admin/login/",
            RedirectView.as_view(
                url="/oidc/authenticate/?next=/admin/",
                permanent=False,
            ),
            name="admin_login",
        ),
        path(
            "admin/logout/",
            RedirectView.as_view(
                url="/oidc/logout/?next=/admin/",
                permanent=False,
            ),
            name="admin_logout",
        ),
    ]

if settings.DEBUG:
    urlpatterns += [
        path("404/", http_404, name="404"),
        path("500/", http_500, name="500"),
    ]
