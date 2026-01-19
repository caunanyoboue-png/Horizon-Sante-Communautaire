# Documentation Technique - ONG ADJAHI Platform

## Vue d'ensemble
Plateforme de gestion hospitalière et communautaire pour l'ONG ADJAHI.
Ce projet permet la gestion des patients, le suivi médical (VIH/TB, CPN), la prise de rendez-vous et le reporting.

## Architecture
Le projet est construit sur **Django 5.x** (Python) avec une base de données MySQL.

### Applications Principales
- **accounts**: Gestion des utilisateurs, rôles (RBAC) et profils.
- **patients**: Dossiers médicaux, rendez-vous, prescriptions.
- **community**: Suivi communautaire (VAD, sensibilisation).
- **messaging**: Messagerie interne sécurisée.
- **reports**: Génération de rapports PDF/Excel.
- **audit**: Logs de sécurité et traçabilité.

### Flux de Données
1. **Authentification**: Login Django standard avec rôles étendus (Medical, Admin, Patient).
2. **Permissions**: Basées sur les Groupes Django, synchronisés via Signals (`accounts/signals.py`).
3. **Audit**: Middleware (`audit/middleware.py`) intercepte toutes les requêtes pour logger les accès.

## Installation et Démarrage

### Prérequis
- Python 3.10+
- MySQL Server
- pip

### Configuration
1. Cloner le repo.
2. Créer un environnement virtuel : `python -m venv .venv`
3. Installer les dépendances : `pip install -r requirements.txt`
4. Configurer `.env` (voir `.env.example`).

### Commandes Utiles
- **Lancer le serveur**: `python manage.py runserver`
- **Tests**: `python manage.py test tests`
- **Anonymisation RGPD**: `python manage.py anonymize_patients --years 5`
- **Envoi Rappels SMS**: `python manage.py send_rdv_sms`

## Sécurité
- **RGPD**: Anonymisation des inactifs, purge des logs (`purge_data`).
- **Audit**: Traçabilité complète des actions (Création, Modif, Accès).
- **Session**: Expiration automatique après 1h d'inactivité.

## Auteurs
Développé pour l'ONG ADJAHI.
