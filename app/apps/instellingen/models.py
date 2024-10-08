from django.contrib.gis.db import models
from encrypted_model_fields.fields import EncryptedCharField
from utils.models import BasisModel


class Instelling(BasisModel):
    mor_core_basis_url = models.URLField(default="http://core.mor.local:8002")
    mor_core_gebruiker_email = models.EmailField()
    mor_core_gebruiker_wachtwoord = EncryptedCharField(max_length=100)
    mor_core_token_timeout = models.PositiveIntegerField(default=0)
    taakr_basis_url = models.URLField(default="http://taakr.mor.local:8009")
    onderwerpen_basis_url = models.URLField(default="http://onderwerpen.mor.local:8006")
    email_beheer = models.EmailField()

    @classmethod
    def actieve_instelling(cls):
        return cls.objects.first()

    def valideer_url(self, veld, url):
        if veld not in (
            "mor_core_basis_url",
            "taakr_basis_url",
            "onderwerpen_basis_url",
        ):
            return False
        return url.startswith(getattr(self, veld))
