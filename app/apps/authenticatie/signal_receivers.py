from apps.authenticatie.models import Profiel
from apps.main.services import MORCoreService
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if kwargs.get("raw"):
        return
    if not hasattr(instance, "profiel"):
        Profiel.objects.create(gebruiker=instance)

    MORCoreService().set_gebruiker(
        gebruiker=instance.serialized_instance(),
    )
