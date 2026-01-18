from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Pathologie


@receiver(post_migrate)
def seed_pathologies(sender, **kwargs):
    if getattr(sender, "name", None) != "community":
        return

    defaults = [
        ("VIH", "VIH / Sida"),
        ("TB", "Tuberculose"),
        ("HEPATITES", "Hépatites virales"),
        ("SANTE_MENTALE", "Santé mentale"),
    ]

    for code, nom in defaults:
        Pathologie.objects.get_or_create(code=code, defaults={"nom": nom})
