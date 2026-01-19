
import os
import django
import sys
from django.db import transaction

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "adjahi_platform.settings")
django.setup()

from django.contrib.auth import get_user_model
from accounts.forms import PatientSignUpForm
from accounts.models import Profil
from patients.models import Patient

User = get_user_model()

def test_registration():
    print("Testing registration...")
    
    # Simulate form data
    form_data = {
        "username": "test_patient_001",
        "first_name": "Jean",
        "last_name": "Test",
        "email": "jean.test@example.com",
        "telephone": "0102030405",
        "password": "password123", # UserCreationForm usually handles password separately in tests, but let's try manual simulation
    }
    
    # Clean up if exists
    User.objects.filter(username="test_patient_001").delete()
    
    try:
        # Manually doing what the form does
        with transaction.atomic():
            print("Creating user...")
            user = User(
                username=form_data["username"],
                first_name=form_data["first_name"],
                last_name=form_data["last_name"],
                email=form_data["email"]
            )
            user.set_password("password123")
            user.save()
            print(f"User created: {user.id}")
            
            print("Checking profile...")
            # Signal should have created profile
            profil = Profil.objects.get(user=user)
            print(f"Profile found: {profil.id}, role: {profil.role}")
            
            # Form logic updates profile
            profil.role = Profil.ROLE_PATIENT
            profil.telephone = form_data["telephone"]
            profil.save()
            print("Profile updated.")
            
            # Form logic creates Patient
            print("Creating patient...")
            import uuid
            code = f"P-{uuid.uuid4().hex[:6].upper()}"
            patient, created = Patient.objects.get_or_create(
                user=user,
                defaults={
                    "code_patient": code,
                    "nom": user.last_name,
                    "prenoms": user.first_name,
                    "telephone": form_data["telephone"],
                },
            )
            print(f"Patient created: {patient.id}, code: {patient.code_patient}")
            
        print("SUCCESS: Registration flow completed without errors.")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_registration()
