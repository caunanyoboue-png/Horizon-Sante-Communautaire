from django import forms

from .models import Consultation, LigneOrdonnance, Ordonnance, Patient, RendezVous, SuiviCPN


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "code_patient",
            "nom",
            "prenoms",
            "date_naissance",
            "sexe",
            "telephone",
            "adresse",
            "zone",
            "antecedents",
        ]
        widgets = {
            "date_naissance": forms.DateInput(attrs={"type": "date"}),
        }


class SuiviCPNForm(forms.ModelForm):
    class Meta:
        model = SuiviCPN
        fields = ["numero", "date", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class RendezVousForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ["date_heure", "objet", "statut"]
        widgets = {
            "date_heure": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ["date_consultation", "motif", "observation"]
        widgets = {
            "date_consultation": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class OrdonnanceForm(forms.ModelForm):
    class Meta:
        model = Ordonnance
        fields = ["date", "diagnostic", "instructions"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class LigneOrdonnanceForm(forms.ModelForm):
    class Meta:
        model = LigneOrdonnance
        fields = ["medicament", "posologie", "duree", "commentaire"]
