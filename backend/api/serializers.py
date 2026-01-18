from rest_framework import serializers

from community.models import DossierCommunautaire, Pathologie, SuiviCommunautaire
from messaging.models import Message, Notification, Thread
from patients.models import Consultation, LigneOrdonnance, Ordonnance, Patient, RendezVous, SuiviCPN


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "id",
            "code_patient",
            "nom",
            "prenoms",
            "date_naissance",
            "sexe",
            "telephone",
            "adresse",
            "zone",
            "antecedents",
            "created_at",
            "updated_at",
        ]


class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = ["id", "patient", "date_consultation", "motif", "observation", "created_at"]


class SuiviCPNSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuiviCPN
        fields = ["id", "patient", "numero", "date", "notes", "created_at"]


class RendezVousSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendezVous
        fields = ["id", "patient", "date_heure", "objet", "statut", "created_at"]


class LigneOrdonnanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneOrdonnance
        fields = ["id", "ordonnance", "medicament", "posologie", "duree", "commentaire"]


class OrdonnanceSerializer(serializers.ModelSerializer):
    lignes = LigneOrdonnanceSerializer(many=True, read_only=True)

    class Meta:
        model = Ordonnance
        fields = [
            "id",
            "patient",
            "date",
            "diagnostic",
            "instructions",
            "created_at",
            "lignes",
        ]


class PathologieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pathologie
        fields = ["id", "code", "nom"]


class SuiviCommunautaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuiviCommunautaire
        fields = ["id", "dossier", "date", "traitement", "observation", "created_at"]


class DossierCommunautaireSerializer(serializers.ModelSerializer):
    suivis = SuiviCommunautaireSerializer(many=True, read_only=True)

    class Meta:
        model = DossierCommunautaire
        fields = [
            "id",
            "patient",
            "pathologie",
            "date_diagnostic",
            "statut",
            "notes",
            "created_at",
            "suivis",
        ]


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ["id", "sujet", "participants", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "thread", "sender", "contenu", "created_at"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "user", "type", "titre", "corps", "url", "lu", "created_at"]
