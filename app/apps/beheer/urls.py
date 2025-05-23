from apps.authenticatie.views import (
    GebruikerAanmakenView,
    GebruikerAanpassenView,
    GebruikerLijstView,
    GebruikerTerughalenView,
    GebruikerVerwijderenView,
    gebruiker_bulk_import,
)
from apps.authorisatie.views import (
    RechtengroepAanmakenView,
    RechtengroepAanpassenView,
    RechtengroepLijstView,
    RechtengroepVerwijderenView,
)
from apps.beheer.views import MORCoreNotificatieStatusOverzicht, beheer
from apps.context.views import (
    ContextAanmakenView,
    ContextAanpassenView,
    ContextLijstView,
    ContextVerwijderenView,
)
from apps.release_notes.views import (
    ReleaseNoteAanmakenView,
    ReleaseNoteAanpassenView,
    ReleaseNoteListView,
    ReleaseNoteVerwijderenView,
)
from apps.taken.views import (
    TaaktypeAanmakenView,
    TaaktypeAanpassenView,
    TaaktypeLijstView,
)
from django.urls import path

urlpatterns = [
    path("", beheer, name="beheer"),
    path(
        "notificatie-status-overzicht/",
        MORCoreNotificatieStatusOverzicht.as_view(),
        name="notificatie_status_overzicht",
    ),
    path("gebruiker/", GebruikerLijstView.as_view(), name="gebruiker_lijst"),
    path(
        "gebruiker/bulk-import/",
        gebruiker_bulk_import,
        name="gebruiker_bulk_import",
    ),
    path(
        "gebruiker/aanmaken/",
        GebruikerAanmakenView.as_view(),
        name="gebruiker_aanmaken",
    ),
    path(
        "gebruiker/<int:pk>/aanpassen/",
        GebruikerAanpassenView.as_view(),
        name="gebruiker_aanpassen",
    ),
    path(
        "gebruiker/<int:pk>/verwijderen/",
        GebruikerVerwijderenView.as_view(),
        name="gebruiker_verwijderen",
    ),
    path(
        "gebruiker/<int:pk>/terughalen/",
        GebruikerTerughalenView.as_view(),
        name="gebruiker_terughalen",
    ),
    path("context/", ContextLijstView.as_view(), name="context_lijst"),
    path(
        "context/aanmaken/",
        ContextAanmakenView.as_view(),
        name="context_aanmaken",
    ),
    path(
        "context/<int:pk>/aanpassen/",
        ContextAanpassenView.as_view(),
        name="context_aanpassen",
    ),
    path(
        "context/<int:pk>/verwijderen/",
        ContextVerwijderenView.as_view(),
        name="context_verwijderen",
    ),
    path("taaktype/", TaaktypeLijstView.as_view(), name="taaktype_lijst"),
    path(
        "taaktype/aanmaken/",
        TaaktypeAanmakenView.as_view(),
        name="taaktype_aanmaken",
    ),
    path(
        "taaktype/<int:pk>/aanpassen/",
        TaaktypeAanpassenView.as_view(),
        name="taaktype_aanpassen",
    ),
    path(
        "rechtengroep/",
        RechtengroepLijstView.as_view(),
        name="rechtengroep_lijst",
    ),
    path(
        "rechtengroep/aanmaken/",
        RechtengroepAanmakenView.as_view(),
        name="rechtengroep_aanmaken",
    ),
    path(
        "rechtengroep/<int:pk>/aanpassen/",
        RechtengroepAanpassenView.as_view(),
        name="rechtengroep_aanpassen",
    ),
    path(
        "rechtengroep/<int:pk>/verwijderen/",
        RechtengroepVerwijderenView.as_view(),
        name="rechtengroep_verwijderen",
    ),
    # Release notes
    path(
        "release-notes/",
        ReleaseNoteListView.as_view(),
        name="release_note_lijst",
    ),
    path(
        "release-notes/aanmaken/",
        ReleaseNoteAanmakenView.as_view(),
        name="release_note_aanmaken",
    ),
    path(
        "release-notes/<int:pk>/aanpassen/",
        ReleaseNoteAanpassenView.as_view(),
        name="release_note_aanpassen",
    ),
    path(
        "release-notes/<int:pk>/verwijderen/",
        ReleaseNoteVerwijderenView.as_view(),
        name="release_note_verwijderen",
    ),
]
