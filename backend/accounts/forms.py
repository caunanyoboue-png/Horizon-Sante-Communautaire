from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.db import transaction
import uuid

from .models import Profil
from patients.models import Patient

User = get_user_model()

class PatientSignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Prénoms", max_length=150, required=True)
    last_name = forms.CharField(label="Nom", max_length=150, required=True)
    telephone = forms.CharField(label="Téléphone", max_length=30, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            profil, _ = Profil.objects.get_or_create(user=user)
            profil.role = Profil.ROLE_PATIENT
            profil.telephone = self.cleaned_data["telephone"]
            profil.save()
            code = f"P-{uuid.uuid4().hex[:6].upper()}"
            Patient.objects.get_or_create(
                user=user,
                defaults={
                    "code_patient": code,
                    "nom": user.last_name,
                    "prenoms": user.first_name,
                    "telephone": self.cleaned_data["telephone"],
                },
            )
        return user
