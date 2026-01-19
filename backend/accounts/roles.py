# Définition centralisée des rôles et des permissions associées

from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from patients.models import Consultation, Ordonnance, Patient, RendezVous, SuiviCPN


@dataclass(frozen=True)
class RoleDefinition:
    code: str
    label: str
    model_perms: dict[type, list[str]]


ROLE_DEFINITIONS: list[RoleDefinition] = [
    RoleDefinition(
        code="ADMIN",
        label="Administrateur",
        model_perms={
            Patient: ["add", "change", "view", "delete"],
            SuiviCPN: ["add", "change", "view", "delete"],
            RendezVous: ["add", "change", "view", "delete"],
            Consultation: ["add", "change", "view", "delete"],
            Ordonnance: ["add", "change", "view", "delete"],
        },
    ),
    RoleDefinition(
        code="MEDECIN",
        label="Médecin",
        model_perms={
            Patient: ["add", "change", "view"],
            SuiviCPN: ["add", "change", "view"],
            RendezVous: ["add", "change", "view"],
            Consultation: ["add", "change", "view"],
            Ordonnance: ["add", "change", "view"],
        },
    ),
    RoleDefinition(
        code="SAGE_FEMME",
        label="Sage-femme",
        model_perms={
            Patient: ["add", "change", "view"],
            SuiviCPN: ["add", "change", "view"],
            RendezVous: ["add", "change", "view"],
            Consultation: ["add", "change", "view"],
            Ordonnance: ["add", "view"],
        },
    ),
    RoleDefinition(
        code="AGENT_COMMUNAUTAIRE",
        label="Agent communautaire",
        model_perms={
            Patient: ["add", "view"],
            SuiviCPN: ["view"],
            RendezVous: ["add", "change", "view"],
            Consultation: ["view"],
            Ordonnance: ["view"],
        },
    ),
    RoleDefinition(
        code="PSYCHOLOGUE",
        label="Psychologue",
        model_perms={
            Patient: ["view"],
            Consultation: ["add", "view"],
        },
    ),
    RoleDefinition(
        code="PATIENT",
        label="Patient",
        model_perms={},
    ),
]


def ensure_groups_and_permissions() -> None:
    """Crée/maj les groupes et leurs permissions."""

    from audit.models import AuditLog
    from community.models import DossierCommunautaire, Pathologie, SuiviCommunautaire
    from messaging.models import Message, Notification, Thread
    from reports.models import Rapport

    role_extra_model_perms = {
        "ADMIN": {
            AuditLog: ["add", "change", "view", "delete"],
            Pathologie: ["add", "change", "view", "delete"],
            DossierCommunautaire: ["add", "change", "view", "delete"],
            SuiviCommunautaire: ["add", "change", "view", "delete"],
            Rapport: ["add", "change", "view", "delete"],
            Thread: ["add", "change", "view", "delete"],
            Message: ["add", "change", "view", "delete"],
            Notification: ["add", "change", "view", "delete"],
        },
        "MEDECIN": {
            AuditLog: ["view"],
            Pathologie: ["view"],
            DossierCommunautaire: ["add", "change", "view"],
            SuiviCommunautaire: ["add", "change", "view"],
            Rapport: ["add", "view"],
            Thread: ["add", "view"],
            Message: ["add", "view"],
            Notification: ["view"],
        },
        "SAGE_FEMME": {
            AuditLog: ["view"],
            Pathologie: ["view"],
            DossierCommunautaire: ["view"],
            SuiviCommunautaire: ["view"],
            Rapport: ["view"],
            Thread: ["add", "view"],
            Message: ["add", "view"],
            Notification: ["view"],
        },
        "AGENT_COMMUNAUTAIRE": {
            AuditLog: ["view"],
            Pathologie: ["view"],
            DossierCommunautaire: ["add", "change", "view"],
            SuiviCommunautaire: ["add", "change", "view"],
            Rapport: ["view"],
            Thread: ["add", "view"],
            Message: ["add", "view"],
            Notification: ["view"],
        },
        "PSYCHOLOGUE": {
            AuditLog: ["view"],
            Pathologie: ["view"],
            DossierCommunautaire: ["add", "change", "view"],
            SuiviCommunautaire: ["add", "change", "view"],
            Rapport: ["view"],
            Thread: ["add", "view"],
            Message: ["add", "view"],
            Notification: ["view"],
        },
    }

    for role in ROLE_DEFINITIONS:
        group, _ = Group.objects.get_or_create(name=role.code)
        model_perms = dict(role.model_perms)
        model_perms.update(role_extra_model_perms.get(role.code, {}))

        perms_to_set: list[Permission] = []

        for model_cls, actions in model_perms.items():
            ct = ContentType.objects.get_for_model(model_cls)
            for action in actions:
                codename = f"{action}_{model_cls._meta.model_name}"
                perm = Permission.objects.filter(content_type=ct, codename=codename).first()
                if perm:
                    perms_to_set.append(perm)

        group.permissions.set(perms_to_set)
