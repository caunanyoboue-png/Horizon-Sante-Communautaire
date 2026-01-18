# 🏥 ONG ADJAHI - Plateforme de Gestion de Santé Communautaire

## 📋 Description

Plateforme web complète pour la digitalisation des activités de santé de l'ONG ADJAHI (Grand-Bassam, Côte d'Ivoire).
Gestion de 3 653 patients avec focus sur le suivi mère-enfant, VIH/SIDA, tuberculose et santé mentale.

## 🏗️ Architecture Technique

### Stack Technologique
- **Backend**: Django 4.2 + Django REST Framework + Celery
- **Frontend**: React 18 + TypeScript + Tailwind CSS + Vite
- **Base de données**: PostgreSQL 15
- **Cache**: Redis 7
- **Authentification**: JWT + 2FA (TOTP)
- **API SMS**: Twilio / AfricasTalking
- **Storage**: MinIO (S3-compatible)
- **Monitoring**: Sentry + Uptime Kuma
- **CI/CD**: GitHub Actions

### Architecture en Couches
```
├── Frontend (React + TypeScript)
│   ├── Pages (Dashboard, Patients, CPN, Rapports)
│   ├── Components (UI réutilisables)
│   └── Services (API calls)
│
├── Backend API (Django REST Framework)
│   ├── Authentication (JWT + 2FA)
│   ├── Modules métier (Patients, Consultations, CPN)
│   ├── Permissions RBAC
│   └── Tasks asynchrones (Celery)
│
├── Base de données (PostgreSQL)
│   ├── Tables normalisées (3NF)
│   ├── Indexes optimisés
│   └── Migrations versionnées
│
└── Infrastructure
    ├── Redis (cache + Celery broker)
    ├── MinIO (fichiers)
    └── Nginx (reverse proxy)
```

## 🚀 Installation Rapide

### Prérequis
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Git

### 1. Backend Setup

```powershell
# Créer environnement virtuel
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1

# Installer dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Éditer .env avec vos paramètres

# Migrations
python manage.py migrate

# Créer superuser
python manage.py createsuperuser

# Lancer serveur
python manage.py runserver
```

### 2. Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

### 3. Services additionnels

```powershell
# Redis (installer depuis https://github.com/microsoftarchive/redis/releases)
redis-server

# Celery (dans backend/venv)
celery -A config worker -l info
celery -A config beat -l info
```

## 📚 Documentation

- **API Documentation**: http://localhost:8000/api/docs (Swagger UI)
- **Guide Utilisateur**: `/docs/guide-utilisateur.pdf`
- **Guide Admin**: `/docs/guide-admin.pdf`
- **Architecture**: `/docs/architecture/`

## 👥 Utilisateurs & Rôles

| Rôle | Permissions | Accès |
|------|------------|-------|
| **Administrateur** | Tout | Dashboard admin, gestion utilisateurs, rapports globaux |
| **Médecin** | Consultations, prescriptions | Patients, dossiers médicaux, rapports |
| **Sage-femme** | CPN, accouchements | Suivi prénatal, planning CPN |
| **Agent communautaire** | Saisie terrain | Collecte données, visites domicile |
| **Psychologue** | Santé mentale | Dossiers psychologiques, suivis |
| **Patient** (optionnel) | Lecture seule | Rendez-vous, ordonnances |

## 🔐 Sécurité

- ✅ Authentification JWT avec refresh tokens
- ✅ 2FA obligatoire pour administrateurs
- ✅ Chiffrement AES-256 pour données sensibles
- ✅ HTTPS obligatoire en production
- ✅ CORS configuré
- ✅ Rate limiting (100 req/min par IP)
- ✅ Audit logs de tous les accès
- ✅ Conformité RGPD (consentement, droit à l'oubli)
- ✅ Sauvegardes automatiques quotidiennes

## 🧪 Tests

```powershell
# Backend (pytest)
cd backend
pytest --cov=. --cov-report=html

# Frontend (Vitest)
cd frontend
npm run test
npm run test:coverage

# Tests E2E (Playwright)
npm run test:e2e
```

**Objectif couverture**: >80%

## 📊 Modules Fonctionnels

### 1. Gestion Patients
- Fiche patient complète (identité, antécédents, allergies)
- Historique consultations
- Alertes médicales
- Suivi chronologique

### 2. Suivi Prénatal (CPN)
- CPN1 à CPN4
- Calcul automatique dates prochaines visites
- Alertes SMS 2 semaines avant
- Suivi poids, tension, examens
- Détection grossesses à risque

### 3. Santé Communautaire
- VIH/SIDA (traitement ARV, charge virale)
- Tuberculose (suivi traitement 6 mois)
- Hépatites virales
- Santé mentale (consultations psy)

### 4. Rapports & Statistiques
- Dashboard temps réel
- Indicateurs CPN1-CPN4
- Taux de suivi VIH/TB
- Exports PDF/Excel
- Graphiques interactifs

### 5. Communication
- Messagerie interne
- Notifications push
- Alertes SMS patients
- Rappels automatiques

## 📈 Performance

- **Temps de réponse API**: <500ms (P95)
- **Chargement pages**: <2s
- **Utilisateurs concurrents**: 200+
- **Uptime**: 99.5%

## 🔄 CI/CD Pipeline

```yaml
Commit → Tests unitaires → Tests intégration → Build → Deploy staging → Tests E2E → Deploy prod
```

## 📦 Déploiement Production

### Option 1: Docker Compose (Recommandé)
```powershell
docker-compose up -d
```

### Option 2: Serveur dédié
Voir `/docs/deployment-guide.md`

### Hébergement recommandé
- **OVH VPS**: 16 Go RAM, 4 vCPU (≈40€/mois)
- **DigitalOcean Droplet**: 16 Go RAM (≈96$/mois)
- **AWS Lightsail**: 16 Go RAM (≈96$/mois)

## 📞 Support & Maintenance

- **Hotline**: +225 XX XX XX XX XX
- **Email**: support@ong-adjahi.ci
- **SLA**: Réponse <4h pour bugs critiques
- **Mises à jour**: Mensuelles (patch), trimestrielles (features)

## 🛣️ Roadmap

### Phase 1 (Mois 1-2) - MVP ✅
- [x] Authentification
- [x] Gestion patients
- [x] Module CPN basique
- [x] Dashboard simple

### Phase 2 (Mois 3-4)
- [ ] Notifications SMS
- [ ] Rapports avancés
- [ ] Module VIH/TB complet
- [ ] PWA (offline mode)

### Phase 3 (Mois 5-6)
- [ ] Application mobile (React Native)
- [ ] IA prédictive (risques grossesse)
- [ ] Téléconsultation vidéo
- [ ] Intégration laboratoires

## 📄 Licence

Propriétaire - ONG ADJAHI © 2026

## 👨‍💻 Contributeurs

- **Chef de projet**: À définir
- **Dev Backend**: À définir
- **Dev Frontend**: À définir
- **DevOps**: À définir
- **QA Tester**: À définir

---

**Version**: 1.0.0  
**Dernière mise à jour**: 18/01/2026  
**Statut**: 🟢 En développement
