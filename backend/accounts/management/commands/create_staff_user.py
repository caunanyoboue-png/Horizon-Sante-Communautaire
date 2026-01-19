from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profil

User = get_user_model()

class Command(BaseCommand):
    help = "Créer un utilisateur staff (Médecin, Sage-femme, Agent, etc.)"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Nom d'utilisateur")
        parser.add_argument("password", type=str, help="Mot de passe")
        parser.add_argument("role", type=str, choices=[c[0] for c in Profil.ROLE_CHOICES], help="Rôle (MEDECIN, SAGE_FEMME, ADMIN, etc.)")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        role = options["role"]

        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Utilisateur {username} créé."))
        else:
            self.stdout.write(self.style.WARNING(f"Utilisateur {username} existe déjà. Mise à jour du rôle."))

        # Le signal post_save crée le profil, mais on s'assure qu'il est à jour
        profil, _ = Profil.objects.get_or_create(user=user)
        profil.role = role
        profil.save()
        
        # Le signal post_save de Profil synchronise les groupes
        
        self.stdout.write(self.style.SUCCESS(f"Rôle {role} attribué à {username}."))
