from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Profil
from .roles import ensure_groups_and_permissions

User = get_user_model()


@receiver(post_save, sender=User)
def create_profil_for_user(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(user=instance)


@receiver(post_save, sender=Profil)
def sync_user_group_with_role(sender, instance, **kwargs):
    # Synchronise l'appartenance au groupe correspondant au rôle
    if not instance.user_id:
        return

    # Retire l'utilisateur des groupes de rôles connus puis ajoute le bon
    role_codes = ["ADMIN", "MEDECIN", "SAGE_FEMME", "AGENT_COMMUNAUTAIRE", "PSYCHOLOGUE"]
    instance.user.groups.remove(*Group.objects.filter(name__in=role_codes))
    group = Group.objects.filter(name=instance.role).first()
    if group:
        instance.user.groups.add(group)


@receiver(post_migrate)
def ensure_role_groups(sender, **kwargs):
    # On attend que l'app patients ait terminé, car les permissions sont créées
    # lors du post_migrate de chaque app (ordre = INSTALLED_APPS).
    if getattr(sender, "name", None) not in ("patients", "community", "reports", "messaging", "audit"):
        return
    ensure_groups_and_permissions()
