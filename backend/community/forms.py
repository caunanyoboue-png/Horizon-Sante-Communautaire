from django import forms

from .models import DossierCommunautaire, SuiviCommunautaire


class DossierCommunautaireForm(forms.ModelForm):
    class Meta:
        model = DossierCommunautaire
        fields = ["patient", "pathologie", "date_diagnostic", "statut", "notes"]
        widgets = {
            "date_diagnostic": forms.DateInput(attrs={"type": "date"}),
        }


class SuiviCommunautaireForm(forms.ModelForm):
    class Meta:
        model = SuiviCommunautaire
        fields = ["date", "traitement", "observation"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class VIHSuiviForm(SuiviCommunautaireForm):
    pass


class TBSuiviForm(SuiviCommunautaireForm):
    pass


class HepatiteSuiviForm(SuiviCommunautaireForm):
    pass


class SanteMentaleSuiviForm(SuiviCommunautaireForm):
    pass
