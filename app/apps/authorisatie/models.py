from django.contrib.gis.db import models


class BasisPermissie:
    naam = None
    codenaam = None


class TaakBekijkenPermissie(BasisPermissie):
    naam = "Taak bekijken"
    codenaam = "taak_bekijken"


class TakenLijstBekijkenPermissie(BasisPermissie):
    naam = "Taken lijst bekijken"
    codenaam = "taken_lijst_bekijken"


class TaakAanmakenPermissie(BasisPermissie):
    naam = "Taak aanmaken"
    codenaam = "taak_aanmaken"


class TaakAfrondenPermissie(BasisPermissie):
    naam = "Taak afronden"
    codenaam = "taak_afronden"


class GebruikerLijstBekijkenPermissie(BasisPermissie):
    naam = "Gebruiker lijst bekijken"
    codenaam = "gebruiker_lijst_bekijken"


class GebruikerAanmakenPermissie(BasisPermissie):
    naam = "Gebruiker aanmaken"
    codenaam = "gebruiker_aanmaken"


class GebruikerBekijkenPermissie(BasisPermissie):
    naam = "Gebruiker bekijken"
    codenaam = "gebruiker_bekijken"


class GebruikerAanpassenPermissie(BasisPermissie):
    naam = "Gebruiker aanpassen"
    codenaam = "gebruiker_aanpassen"


class GebruikerVerwijderenPermissie(BasisPermissie):
    naam = "Gebruiker verwijderen"
    codenaam = "gebruiker_verwijderen"


class GebruikersgroepToekennenPermissie(BasisPermissie):
    naam = "Gebruikersgroep toekennen/verwijderen voor een gebruiker"
    codenaam = "gebruikersgroep_toekennen_verwijderen"


class GebruikersgroepAanmakenPermissie(BasisPermissie):
    naam = "Gebruikersgroep aanmaken"
    codenaam = "gebruikersgroep_aanmaken"


class GebruikersgroepBekijkenPermissie(BasisPermissie):
    naam = "Gebruikersgroep bekijken"
    codenaam = "gebruikersgroep_bekijken"


class GebruikersgroepVerwijderenPermissie(BasisPermissie):
    naam = "Gebruikersgroep verwijderen"
    codenaam = "gebruikersgroep_verwijderen"


class BeheerBekijkenPermissie(BasisPermissie):
    naam = "Beheer bekijken"
    codenaam = "beheer_bekijken"


class TaaktypeLijstBekijkenPermissie(BasisPermissie):
    naam = "Taaktype lijst bekijken"
    codenaam = "taaktype_lijst_bekijken"


class TaaktypeAanmakenPermissie(BasisPermissie):
    naam = "Taaktype aanmaken"
    codenaam = "taaktype_aanmaken"


class TaaktypeBekijkenPermissie(BasisPermissie):
    naam = "Taaktype bekijken"
    codenaam = "taaktype_bekijken"


class TaaktypeAanpassenPermissie(BasisPermissie):
    naam = "Taaktype aanpassen"
    codenaam = "taaktype_aanpassen"


class ContextLijstBekijkenPermissie(BasisPermissie):
    naam = "Context lijst bekijken"
    codenaam = "context_lijst_bekijken"


class ContextAanmakenPermissie(BasisPermissie):
    naam = "Context aanmaken"
    codenaam = "context_aanmaken"


class ContextBekijkenPermissie(BasisPermissie):
    naam = "Context bekijken"
    codenaam = "context_bekijken"


class ContextAanpassenPermissie(BasisPermissie):
    naam = "Context aanpassen"
    codenaam = "context_aanpassen"


gebruikersgroep_permissies = (
    TakenLijstBekijkenPermissie,
    TaakBekijkenPermissie,
    TaakAanmakenPermissie,
    TaakAfrondenPermissie,
    GebruikerLijstBekijkenPermissie,
    GebruikerAanmakenPermissie,
    GebruikerAanpassenPermissie,
    GebruikerBekijkenPermissie,
    GebruikerVerwijderenPermissie,
    GebruikersgroepToekennenPermissie,
    GebruikersgroepAanmakenPermissie,
    GebruikersgroepBekijkenPermissie,
    GebruikersgroepVerwijderenPermissie,
    BeheerBekijkenPermissie,
    TaaktypeLijstBekijkenPermissie,
    TaaktypeAanmakenPermissie,
    TaaktypeBekijkenPermissie,
    TaaktypeAanpassenPermissie,
    ContextLijstBekijkenPermissie,
    ContextAanmakenPermissie,
    ContextBekijkenPermissie,
    ContextAanpassenPermissie,
)

gebruikersgroep_permissie_opties = [
    (p.codenaam, p.naam) for p in gebruikersgroep_permissies
]


class Permissie(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = gebruikersgroep_permissie_opties
