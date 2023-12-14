from apps.authenticatie.views import (
    GebruikerAanmakenView,
    GebruikerAanpassenView,
    GebruikerLijstView,
)
from apps.authorisatie.views import (
    RechtengroepAanmakenView,
    RechtengroepAanpassenView,
    RechtengroepLijstView,
    RechtengroepVerwijderenView,
)
from apps.beheer.views import beheer
from apps.context.views import (
    ContextAanmakenView,
    ContextAanpassenView,
    ContextLijstView,
    ContextVerwijderenView,
)
from apps.main.views import (
    config,
    filter,
    http_404,
    http_500,
    incident_modal_handle,
    informatie,
    kaart_modus,
    meldingen_bestand,
    root,
    sorteer_filter,
    taak_detail,
    taak_toewijzen,
    taak_toewijzing_intrekken,
    taken_afgerond_overzicht,
    taken_lijst,
    taken_overzicht,
    ui_settings_handler,
)
from apps.release_notes.views import (
    ReleaseNoteAanmakenView,
    ReleaseNoteAanpassenView,
    ReleaseNoteDetailView,
    ReleaseNoteListView,
    ReleaseNoteListViewPublic,
    ReleaseNoteVerwijderenView,
)
from apps.taken.views import (
    TaaktypeAanmakenView,
    TaaktypeAanpassenView,
    TaaktypeLijstView,
)
from apps.taken.viewsets import TaaktypeViewSet, TaakViewSet
from django.conf import settings
from django.conf.urls.static import static
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
    path("informatie/", informatie, name="informatie"),
    path("api/v1/", include((router.urls, "app"), namespace="v1")),
    path("api-token-auth/", views.obtain_auth_token),
    path("admin/", admin.site.urls),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("config/", config, name="config"),
    path("health/", include("health_check.urls")),
    # START taken
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
    path("sorteer-filter/", sorteer_filter, name="sorteer_filter"),
    path("kaart-modus/", kaart_modus, name="kaart_modus"),
    path("taak/<int:id>/", taak_detail, name="taak_detail"),
    path("taak-toewijzen/<int:id>/", taak_toewijzen, name="taak_toewijzen"),
    path(
        "taak-toewijzing-intrekken/<int:id>/",
        taak_toewijzing_intrekken,
        name="taak_toewijzing_intrekken",
    ),
    # END taken
    # START partials
    path("part/pageheader-form/", ui_settings_handler, name="pageheader_form_part"),
    path("part/filter/<str:status>/", filter, name="filter_part"),
    path("part/taken/<str:status>/", taken_lijst, name="taken_lijst_part"),
    path(
        "part/taak-modal-handle/<int:id>/",
        incident_modal_handle,
        name="incident_modal_handle_part",
    ),
    # END partials
    # START beheer
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
    path("beheer/context/", ContextLijstView.as_view(), name="context_lijst"),
    path(
        "beheer/context/aanmaken/",
        ContextAanmakenView.as_view(),
        name="context_aanmaken",
    ),
    path(
        "beheer/context/<int:pk>/aanpassen/",
        ContextAanpassenView.as_view(),
        name="context_aanpassen",
    ),
    path(
        "beheer/context/<int:pk>/verwijderen/",
        ContextVerwijderenView.as_view(),
        name="context_verwijderen",
    ),
    path("beheer/taaktype/", TaaktypeLijstView.as_view(), name="taaktype_lijst"),
    path(
        "beheer/taaktype/aanmaken/",
        TaaktypeAanmakenView.as_view(),
        name="taaktype_aanmaken",
    ),
    path(
        "beheer/taaktype/<int:pk>/aanpassen/",
        TaaktypeAanpassenView.as_view(),
        name="taaktype_aanpassen",
    ),
    path(
        "beheer/rechtengroep/",
        RechtengroepLijstView.as_view(),
        name="rechtengroep_lijst",
    ),
    path(
        "beheer/rechtengroep/aanmaken/",
        RechtengroepAanmakenView.as_view(),
        name="rechtengroep_aanmaken",
    ),
    path(
        "beheer/rechtengroep/<int:pk>/aanpassen/",
        RechtengroepAanpassenView.as_view(),
        name="rechtengroep_aanpassen",
    ),
    path(
        "beheer/rechtengroep/<int:pk>/verwijderen/",
        RechtengroepVerwijderenView.as_view(),
        name="rechtengroep_verwijderen",
    ),
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
    path(
        "beheer/release-notes/",
        ReleaseNoteListView.as_view(),
        name="release_note_lijst",
    ),
    path(
        "beheer/release-notes/aanmaken/",
        ReleaseNoteAanmakenView.as_view(),
        name="release_note_aanmaken",
    ),
    path(
        "beheer/release-notes/<int:pk>/aanpassen/",
        ReleaseNoteAanpassenView.as_view(),
        name="release_note_aanpassen",
    ),
    path(
        "beheer/release-notes/<int:pk>/verwijderen/",
        ReleaseNoteVerwijderenView.as_view(),
        name="release_note_verwijderen",
    ),
    # END beheer
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
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("404/", http_404, name="404"),
        path("500/", http_500, name="500"),
    ]
