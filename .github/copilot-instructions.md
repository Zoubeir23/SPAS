# SPAS - Instructions pour Agents IA

## Architecture Générale

**SPAS** (Système Prédictif d'Alerte Scolaire) est une application full-stack pour identifier les étudiants à risque d'abandon scolaire via ML.

- **Frontend** : React 18 + TypeScript + Vite (`frontend/`) - 100% implémenté avec données mockées
- **Backend** : Django 5 + DRF + PostgreSQL (`backend/`) - API REST avec 10 apps Django, 14 ViewSets
- **ML** : scikit-learn pour prédictions de risque d'abandon

## Stack et Conventions

### Frontend (`frontend/src/`)

- **État global** : Zustand (`store/authStore.ts`)
- **API** : Services mockés dans `api/services/` - à connecter à l'API Django
- **Routing** : React Router avec routes protégées (`routes/RouteProtegee.tsx`)
- **Formulaires** : React Hook Form + Zod pour validation
- **Alias d'import** : `@/` pointe vers `src/` (voir `vite.config.ts`)
- **Nommage pages** : Français (`Connexion.tsx`, `ListeEtudiants.tsx`, `TableauDeBordGeneral.tsx`)

### Backend (`backend/apps/`)

Les 10 apps Django (authentication + 9 domaine) suivent cette structure :

```
apps/{app_name}/
├── models.py          # Modèles Django
├── serializers.py     # DRF Serializers (List, Detail, Create variantes)
├── views.py           # ViewSets avec actions personnalisées
├── urls.py            # Routes avec DefaultRouter
├── admin.py           # Configuration admin
└── migrations/        # Migrations Django
```

**Conventions clés :**

- User model custom avec email comme identifiant (pas de username)
- Rôles utilisateur : `admin`, `teacher`, `ds`, `pedagogical`
- Niveaux de risque étudiant : `low`, `medium`, `high`
- JWT pour authentification via `apps/authentication/`

## Commandes de Développement

### Frontend

```bash
cd frontend
npm run dev        # Serveur dev (port 5173)
npm run build      # Build production
npm run test       # Tests Vitest
npm run lint       # ESLint
```

### Backend

```bash
cd backend
# Activer venv: venv\Scripts\activate (Windows)
python manage.py runserver              # API (port 8000)
python manage.py migrate                # Appliquer migrations
python manage.py init_spas              # Créer données de test
python manage.py createsuperuser        # Admin Django
pytest                                  # Tests
```

### Services requis (backend)

- PostgreSQL 14+ (`DB_NAME=spas_db`)
- Redis 7+ (pour Celery - optionnel en dev)

## Points d'Intégration Frontend/Backend

Les services frontend (`frontend/src/api/services/`) sont **mockés** et doivent être connectés à l'API Django :

| Service Frontend       | Endpoint Backend    |
| ---------------------- | ------------------- |
| `authService.ts`       | `/api/auth/`        |
| `studentService.ts`    | `/api/students/`    |
| `programService.ts`    | `/api/programs/`    |
| `predictionService.ts` | `/api/predictions/` |
| `alertService.ts`      | `/api/alerts/`      |

## Patterns à Respecter

### Créer un nouveau ViewSet Backend

Voir `backend/apps/students/views.py` comme référence :

- Utiliser `ModelViewSet` avec `IsAuthenticated`
- Ajouter filtres : `DjangoFilterBackend`, `SearchFilter`, `OrderingFilter`
- Optimiser queryset avec `select_related` et `prefetch_related`
- Actions custom avec `@action(detail=True/False)`

### Créer un Serializer

Utiliser des variantes selon le contexte (voir `backend/apps/students/serializers.py`) :

- `StudentListSerializer` - champs minimaux pour listes
- `StudentSerializer` - complet pour détail/création

### Ajouter une page Frontend

1. Créer composant dans `frontend/src/pages/{module}/`
2. Ajouter route dans `frontend/src/routes/index.tsx`
3. Mettre à jour constantes dans `frontend/src/utils/constants.ts`

## Documentation Clé

- [API_GUIDE.md](../backend/API_GUIDE.md) - Documentation complète des endpoints
- [STRUCTURE_BACKEND.md](../backend/STRUCTURE_BACKEND.md) - Architecture détaillée du backend
- [Architecture/Architecture.txt](../Architecture/Architecture.txt) - Mapping composants UI vers fichiers

## Documentation API

- Swagger UI : `http://localhost:8000/api/docs/`
- ReDoc : `http://localhost:8000/api/redoc/`
- Admin Django : `http://localhost:8000/admin/`
