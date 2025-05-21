from apps.aliassen.views import MeldingNotificatieAPIView
from apps.authenticatie.views import (
    GebruikerProfielView,
    LoginView,
    LogoutView,
    OnboardingView,
)
from apps.health.views import healthz
from apps.main.views import (
    HomepageView,
    clear_melding_token_from_cache,
    config,
    http_403,
    http_404,
    http_410,
    http_500,
    infosheet_mock,
    kaart_modus,
    meldingen_bestand,
    meldingen_bestand_protected,
    navigeer,
    root,
    sorteer_filter,
    taak_afhandelen,
    taak_delen,
    taak_detail,
    taak_detail_melding_tijdlijn,
    taak_detail_preview,
    taak_toewijzen,
    taak_toewijzing_intrekken,
    taak_zoeken,
    taken,
    taken_filter,
    taken_lijst,
    ui_settings_handler,
)
from apps.release_notes.views import (
    ReleaseNoteDetailView,
    ReleaseNoteListViewPublic,
    SnackOverzichtStreamView,
    SnackOverzichtView,
    SnackView,
    ToastView,
)
from apps.taken.views import TaakRTaaktypeView
from apps.taken.viewsets import TaaktypeViewSet, TaakViewSet
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django_select2 import urls as select2_urls
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
    # Tijdelijke url voor nieuwe homepage
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    path(
        "home/",
        HomepageView.as_view(),
        name="home",
    ),
    path("api/v1/", include((router.urls, "app"), namespace="v1")),
    path(
        "api/v1/melding/",
        MeldingNotificatieAPIView.as_view(),
        name="melding_notificatie",
    ),
    path("api-token-auth/", views.obtain_auth_token),
    path(
        "admin/clear-melding-token-from-cache/",
        clear_melding_token_from_cache,
        name="clear_melding_token_from_cache",
    ),
    path("config/", config, name="config"),
    path("health/", include("health_check.urls")),
    path("healthz/", healthz, name="healthz"),
    # START taken
    path(
        "taken/",
        taken,
        name="taken",
    ),
    path(
        "taken/filter/",
        taken_filter,
        name="taken_filter",
    ),
    path(
        "taken/lijst/",
        taken_lijst,
        name="taken_lijst",
    ),
    path("sorteer-filter/", sorteer_filter, name="sorteer_filter"),
    path("taak-zoeken/", taak_zoeken, name="taak_zoeken"),
    path("kaart-modus/", kaart_modus, name="kaart_modus"),
    path("taak/<int:id>/", taak_detail, name="taak_detail"),
    path(
        "taak/<int:id>/melding-tijdlijn",
        taak_detail_melding_tijdlijn,
        name="taak_detail_melding_tijdlijn",
    ),
    path(
        "taak/<int:id>/delen/<str:signed_data>/",
        taak_detail_preview,
        name="taak_detail_preview",
    ),
    path(
        "taak/<int:id>/delen/",
        taak_delen,
        name="taak_delen",
    ),
    path("taak-toewijzen/<int:id>/", taak_toewijzen, name="taak_toewijzen"),
    path(
        "taak-toewijzing-intrekken/<int:id>/",
        taak_toewijzing_intrekken,
        name="taak_toewijzing_intrekken",
    ),
    # Gebruikers
    path(
        "gebruiker/profiel/",
        GebruikerProfielView.as_view(),
        name="gebruiker_profiel",
    ),
    # END taken
    # sidesheet
    path(
        "infosheet-mock/",
        infosheet_mock,
        name="infosheet_mock",
    ),
    path(
        "taaktype/<int:pk>/taakr/", TaakRTaaktypeView.as_view(), name="taaktype_taakr"
    ),
    # START partials
    path("part/pageheader-form/", ui_settings_handler, name="pageheader_form_part"),
    path("navigeer/<str:lat>/<str:long>/", navigeer, name="navigeer"),
    path(
        "taak/<int:id>/afhandelen/",
        taak_afhandelen,
        name="taak_afhandelen",
    ),
    # END partials
    path("onboarding/", OnboardingView.as_view(), name="onboarding"),
    # Release notes
    path(
        "release-notes/",
        ReleaseNoteListViewPublic.as_view(),
        name="release_note_lijst_public",
    ),
    path(
        "release-notes/<int:pk>/",
        ReleaseNoteDetailView.as_view(),
        name="release_note_detail",
    ),
    # Notificaties
    path(
        "notificaties/snack/",
        SnackView.as_view(),
        name="snack_lijst",
    ),
    path(
        "notificaties/toast/",
        ToastView.as_view(),
        name="toast_lijst",
    ),
    path(
        "notificaties/snack/overzicht/",
        SnackOverzichtView.as_view(),
        name="snack_overzicht",
    ),
    path(
        "notificaties/snack/overzicht/stream/",
        SnackOverzichtStreamView.as_view(),
        name="snack_overzicht_stream",
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
    path("select2/", include(select2_urls)),
    re_path(r"core/media/", meldingen_bestand, name="meldingen_bestand"),
    re_path(
        r"core-protected/media/",
        meldingen_bestand_protected,
        name="meldingen_bestand_protected",
    ),
    path("beheer/", include("apps.beheer.urls")),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
]

if not settings.ENABLE_DJANGO_ADMIN_LOGIN:
    urlpatterns += [
        path(
            "admin/login/",
            RedirectView.as_view(url="/login/?next=/admin/"),
            name="admin_login",
        ),
        path(
            "admin/logout/",
            RedirectView.as_view(url="/logout/?next=/"),
            name="admin_logout",
        ),
    ]

if settings.OIDC_ENABLED:
    urlpatterns += [
        path("oidc/", include("mozilla_django_oidc.urls")),
    ]

urlpatterns += [
    path("admin/", admin.site.urls),
]

if settings.APP_ENV != "productie":
    urlpatterns += [
        path("403/", http_403, name="403"),
        path("404/", http_404, name="404"),
        path("410/", http_410, name="410"),
        path("500/", http_500, name="500"),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
