# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [1.0.0] - 2024-01-01

### Ajouté

#### Infrastructure
- Configuration Django 5.0 avec Django REST Framework
- Authentification JWT avec Simple JWT
- Configuration PostgreSQL comme base de données
- Configuration Redis et Celery pour tâches asynchrones
- CORS configuré pour frontend React
- Documentation API avec drf-spectacular (OpenAPI 3.0)
- Configuration Docker et docker-compose
- Scripts de setup pour Windows (batch et PowerShell)

#### Apps Django

**users**
- Modèle User personnalisé avec authentification par email
- Rôles utilisateurs: ADMIN, TEACHER, ADVISOR, COORDINATOR
- Endpoints: profil, modification profil, changement mot de passe
- Admin Django configuré

**students**
- Modèle Student avec informations personnelles et académiques
- Statuts: ACTIVE, INACTIVE, GRADUATED, DROPPED
- Endpoints: CRUD complet, recherche, filtres
- Endpoint spécial: étudiants à risque
- Commande management: init_spas pour données de test

**programs**
- Modèles Program et Course
- Gestion des prérequis de cours
- Endpoints: programmes, cours, relations
- Filtres par programme, type de cours

**sessions**
- Modèles: AcademicPeriod, CourseSession, Enrollment
- Gestion des périodes académiques (sessions)
- Inscriptions étudiants aux cours
- Endpoints: périodes, sessions, inscriptions
- Endpoint spécial: période actuelle

**grades**
- Modèles: Grade, CourseGradeSummary
- Système de notes avec poids
- Calcul automatique note finale et GPA
- Conversion en lettres (A+, A, B+, etc.)
- Endpoints: notes, résumés, statistiques
- Endpoint spécial: étudiants en échec

**attendance**
- Modèles: AttendanceRecord, AttendanceSummary
- Statuts de présence: PRESENT, ABSENT, LATE, EXCUSED
- Calcul automatique taux de présence
- Endpoints: enregistrements, résumés, statistiques
- Endpoint spécial: création en masse, faible présence

**ml**
- Modèles: MLModel, TrainingJob
- Gestion de modèles de machine learning
- Métriques: accuracy, precision, recall, F1 score
- Tâches Celery pour entraînement asynchrone
- Endpoints: modèles, activation, entraînement

**predictions**
- Modèles: Prediction, RecommendedIntervention
- Prédictions de risque d'abandon (0-100%)
- Niveaux de risque: LOW, MEDIUM, HIGH, CRITICAL
- Facteurs contributifs: attendance, grades, engagement
- Interventions recommandées avec priorités
- Endpoints: prédictions, statistiques, génération en masse
- Tâches Celery pour génération asynchrone

**alerts**
- Modèles: Alert, AlertAction
- Types d'alertes: dropout risk, attendance, grades, engagement
- Workflow: ACTIVE → ACKNOWLEDGED → RESOLVED
- Assignation et suivi d'alertes
- Actions documentées sur alertes
- Endpoints: alertes, actions, assignation, résolution
- Tâches Celery pour création automatique

#### Documentation
- README.md - Documentation complète
- QUICKSTART.md - Guide de démarrage rapide
- API_GUIDE.md - Documentation API détaillée
- PROJECT_SUMMARY.md - Résumé du projet
- CHANGELOG.md - Historique des versions

#### Tests
- Structure de tests pour chaque app
- Exemples de tests unitaires et d'intégration
- Configuration pytest
- Tests pour models, serializers, views

#### Développement
- Configuration VS Code (settings, launch, extensions)
- Scripts de développement Windows
- Docker et docker-compose pour environnement complet
- Commande init_spas pour données de test

### Sécurité
- JWT authentication avec refresh tokens
- CORS configuré
- Validation des entrées via serializers
- Permissions par rôle utilisateur
- HTTPS en production (settings)
- Gestion sécurisée des secrets via .env

### Performance
- Utilisation de select_related et prefetch_related
- Indexes sur champs fréquemment filtrés
- Pagination par défaut (20 items)
- Tâches asynchrones pour opérations longues

## [Non publié]

### À venir (v1.1.0)
- Rate limiting (throttling) API
- Caching Redis pour endpoints fréquents
- Celery beat pour tâches périodiques
- Export de données (CSV, Excel)
- Notifications email pour alertes critiques
- Dashboard analytics
- Audit logging complet

### À venir (v1.2.0)
- Rapports PDF générés
- Intégration SMS pour notifications
- API GraphQL (optionnel)
- Webhooks pour événements importants
- Tests de charge et optimisations
- Monitoring avec Sentry

### À venir (v2.0.0)
- ML pipeline complet et automatisé
- A/B testing pour interventions
- Recommandations personnalisées
- Intégration avec systèmes externes (SIS)
- Module de gestion de cas
- Analytics prédictif avancé

---

## Types de changements
- `Ajouté` pour les nouvelles fonctionnalités
- `Modifié` pour les changements dans les fonctionnalités existantes
- `Déprécié` pour les fonctionnalités bientôt supprimées
- `Retiré` pour les fonctionnalités supprimées
- `Corrigé` pour les corrections de bugs
- `Sécurité` pour les vulnérabilités corrigées
