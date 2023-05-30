from apps.aliassen.models import BijlageAlias, MeldingAlias
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=BijlageAlias, dispatch_uid="ophalen_bijlagealias_data")
@receiver(pre_save, sender=MeldingAlias, dispatch_uid="ophalen_meldingalias_data")
def ophalen_alias_data(sender, instance, **kwargs):
    if kwargs.get("raw"):
        return
    if not instance.id:
        instance.valideer_bron_url()
