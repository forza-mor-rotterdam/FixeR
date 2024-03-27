from django.contrib.gis.db import models
from encrypted_model_fields.fields import EncryptedCharField
from utils.models import BasisModel


class Instelling(BasisModel):
    mor_core_gebruiker_email = models.EmailField()
    mor_core_gebruiker_wachtwoord = EncryptedCharField(max_length=100)
