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


class GebruikerAanmakenPermissie(BasisPermissie):
    naam = "Gebruiker aanmaken"
    codenaam = "gebruiker_aanmaken"


class GebruikerBekijkenPermissie(BasisPermissie):
    naam = "Gebruiker bekijken"
    codenaam = "gebruiker_bekijken"


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


class MSBPermissie(BasisPermissie):
    naam = "MSB toegang"
    codenaam = "msb_toegang"


gebruikersgroep_permissies = (
    TakenLijstBekijkenPermissie,
    TaakBekijkenPermissie,
    TaakAanmakenPermissie,
    TaakAfrondenPermissie,
    GebruikerAanmakenPermissie,
    GebruikerBekijkenPermissie,
    GebruikerVerwijderenPermissie,
    GebruikersgroepToekennenPermissie,
    GebruikersgroepAanmakenPermissie,
    GebruikersgroepBekijkenPermissie,
    GebruikersgroepVerwijderenPermissie,
)

gebruikersgroep_permissie_opties = [
    (p.codenaam, p.naam) for p in gebruikersgroep_permissies
]


class Permissie(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = gebruikersgroep_permissie_opties
