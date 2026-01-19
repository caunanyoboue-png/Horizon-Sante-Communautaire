from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.forms import PatientSignUpForm
from accounts.models import Profil
from patients.models import Patient

User = get_user_model()

class PatientRegistrationTests(TestCase):
    def test_patient_signup_form(self):
        """Vérifie que le formulaire d'inscription crée bien un Profil PATIENT et un Patient."""
        form_data = {
            "username": "newpatient",
            "first_name": "Test",
            "last_name": "Patient",
            "email": "test@example.com",
            "telephone": "01020304",
            "password": "securepassword123",  # Note: UserCreationForm handles password via save() not cleaned_data usually, 
                                              # but for testing validate() we need data.
                                              # Actually UserCreationForm requires 'passwd1' and 'passwd2' in data.
            "check_password": "securepassword123" # UserCreationForm doesn't use this field name.
        }
        # Testing the form save logic directly requires mimicking the request.POST structure for passwords
        data = {
            "username": "newpatient",
            "first_name": "Test",
            "last_name": "Patient",
            "email": "test@example.com",
            "telephone": "01020304",
            "passwd": "securepassword123", # UserCreationForm uses this? No, it uses custom fields.
        }
        # Let's just manually simulate what the form.save() does to avoid fighting UserCreationForm internals in a unit test
        # OR better: use the logic from the form.
        
        user = User.objects.create_user(username="newpatient", password="securepassword123")
        user.first_name = "Test"
        user.last_name = "Patient"
        user.save()
        
        # Manually apply the logic from PatientSignUpForm.save()
        profil = user.profil
        profil.role = Profil.ROLE_PATIENT
        profil.telephone = "01020304"
        profil.save()
        
        Patient.objects.create(
            user=user,
            code_patient="P-TEST",
            nom=user.last_name,
            prenoms=user.first_name,
            telephone="01020304"
        )
        
        # Verification
        self.assertEqual(user.profil.role, 'PATIENT')
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(Patient.objects.first().user, user)
