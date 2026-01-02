# Authentication Module - SPAS

Module d'authentification sécurisé avec JWT pour le système SPAS (Système Prédictif d'Alerte Scolaire).

## Fonctionnalités

### 1. Inscription et Vérification d'Email
- **Endpoint**: `POST /api/auth/register/`
- Création de compte utilisateur avec vérification d'email obligatoire
- Validation avancée des mots de passe
- Le compte reste inactif jusqu'à la vérification de l'email

**Exemple de requête:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "teacher",
  "phone": "+1234567890"
}
```

### 2. Vérification d'Email
- **Endpoint**: `POST /api/auth/verify-email/`
- Active le compte utilisateur après vérification
- Token expirant après 24 heures

**Exemple de requête:**
```json
{
  "token": "verification_token_here"
}
```

### 3. Renvoi d'Email de Vérification
- **Endpoint**: `POST /api/auth/resend-verification/`
- Rate limiting: 3 demandes par heure

**Exemple de requête:**
```json
{
  "email": "user@example.com"
}
```

### 4. Connexion (Login)
- **Endpoint**: `POST /api/auth/login/`
- Authentification avec email et mot de passe
- Retourne access token et refresh token JWT
- Protection contre le brute force avec verrouillage de compte
- Rate limiting: 5 tentatives par minute

**Exemple de requête:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Réponse:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "teacher"
  }
}
```

### 5. Déconnexion (Logout)
- **Endpoint**: `POST /api/auth/logout/`
- Blacklist le refresh token
- Requiert authentification

**Exemple de requête:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 6. Déconnexion de Tous les Appareils
- **Endpoint**: `POST /api/auth/logout-all/`
- Blacklist tous les tokens actifs de l'utilisateur
- Utile en cas de compromission de compte

### 7. Rafraîchissement de Token
- **Endpoint**: `POST /api/auth/token/refresh/`
- Obtenir un nouveau access token
- Rotation automatique du refresh token
- Rate limiting: 30 demandes par heure

**Exemple de requête:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 8. Vérification de Token
- **Endpoint**: `POST /api/auth/token/verify/`
- Vérifier la validité d'un access token

**Exemple de requête:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 9. Statut de Blacklist de Token
- **Endpoint**: `POST /api/auth/token/blacklist-status/`
- Vérifier si un token est blacklisté

### 10. Réinitialisation de Mot de Passe
**Demande de réinitialisation:**
- **Endpoint**: `POST /api/auth/password/forgot/`
- Rate limiting: 3 demandes par heure

**Exemple de requête:**
```json
{
  "email": "user@example.com"
}
```

**Confirmation de réinitialisation:**
- **Endpoint**: `POST /api/auth/password/reset/`

**Exemple de requête:**
```json
{
  "uid": "encoded_user_id",
  "token": "reset_token",
  "new_password": "NewSecurePass123!"
}
```

### 11. Changement de Mot de Passe
- **Endpoint**: `POST /api/auth/password/change/`
- Requiert authentification
- Validation de l'ancien mot de passe

**Exemple de requête:**
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword123!"
}
```

### 12. Vérification de Force de Mot de Passe
- **Endpoint**: `POST /api/auth/password/check-strength/`
- Retourne score (0-100) et niveau de force

**Exemple de requête:**
```json
{
  "password": "TestPassword123!"
}
```

**Réponse:**
```json
{
  "is_valid": true,
  "score": 85,
  "strength": "excellent",
  "errors": []
}
```

### 13. Informations Utilisateur Actuel
- **Endpoint**: `GET /api/auth/me/`
- Retourne les données de l'utilisateur connecté
- Requiert authentification

### 14. Activité d'Authentification
- **Endpoint**: `GET /api/auth/activity/`
- Historique des 10 derniers événements d'authentification
- Requiert authentification

## Sécurité

### Rate Limiting
- **Login**: 5 tentatives / minute
- **Register**: 3 inscriptions / jour
- **Password Reset**: 3 demandes / heure
- **Email Verification**: 3 renvois / heure
- **Token Refresh**: 30 rafraîchissements / heure

### Protection contre Brute Force
- Verrouillage automatique après 5 tentatives échouées
- Durée de verrouillage: 15 minutes
- Détection et journalisation des activités suspectes

### Validation de Mot de Passe
- Longueur minimale: 8 caractères
- Au moins une majuscule
- Au moins une minuscule
- Au moins un chiffre
- Au moins un caractère spécial
- Détection de patterns communs
- Score de force calculé (0-100)

### JWT Configuration
- **Access Token**: Expire après 60 minutes (configurable)
- **Refresh Token**: Expire après 1 jour (configurable)
- Rotation automatique des refresh tokens
- Blacklist après rotation
- Algorithme: HS256

### Journalisation
Tous les événements d'authentification sont journalisés:
- Connexions réussies/échouées
- Inscriptions
- Vérifications d'email
- Changements de mot de passe
- Réinitialisations de mot de passe
- Déconnexions
- Activités suspectes

## Architecture

### Fichiers Principaux

#### `backends.py`
- Backend d'authentification personnalisé basé sur email
- Intégration avec le système de détection d'activités suspectes

#### `serializers.py`
- Serializers pour toutes les opérations d'authentification
- Validation avancée des entrées

#### `views.py`
- Views API avec documentation OpenAPI
- Gestion des tokens JWT
- Endpoints d'authentification

#### `throttling.py`
- Classes de rate limiting personnalisées
- Détecteur d'activités suspectes
- Système de verrouillage de compte

#### `utils.py`
- Générateur de tokens de vérification d'email
- Validateur de mots de passe avancé
- Service d'envoi d'emails
- Fonctions utilitaires

#### `signals.py`
- Signaux Django pour événements d'authentification
- Journalisation automatique
- Gestion des événements de sécurité

#### `permissions.py`
- Permissions basées sur les rôles
- Contrôle d'accès granulaire

## Configuration Requise

### Variables d'Environnement

```env
# JWT
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1

# Redis (pour cache et blacklist)
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=noreply@spas.com

# Frontend URL (pour liens dans emails)
FRONTEND_URL=http://localhost:5173
```

### Dépendances Python

```txt
djangorestframework-simplejwt
django-redis
redis
```

### Configuration Settings

Ajouter dans `settings.py`:

```python
# Authentication Backend
AUTHENTICATION_BACKENDS = [
    'apps.authentication.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Cache Configuration (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
    }
}
```

## Utilisation avec Frontend

### Headers d'Authentification
```javascript
headers: {
  'Authorization': 'Bearer ' + accessToken,
  'Content-Type': 'application/json'
}
```

### Gestion des Tokens
1. Stocker access et refresh tokens en localStorage/sessionStorage
2. Inclure access token dans toutes les requêtes authentifiées
3. Rafraîchir le token avant expiration
4. Gérer le cas de token expiré (401)

### Exemple de Flux d'Authentification

```javascript
// 1. Inscription
const register = async (userData) => {
  const response = await fetch('/api/auth/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData)
  });
  return response.json();
};

// 2. Connexion
const login = async (email, password) => {
  const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();

  // Stocker les tokens
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);

  return data;
};

// 3. Rafraîchir le token
const refreshToken = async () => {
  const refresh = localStorage.getItem('refresh_token');
  const response = await fetch('/api/auth/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  return data;
};

// 4. Déconnexion
const logout = async () => {
  const refresh = localStorage.getItem('refresh_token');
  await fetch('/api/auth/logout/', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ refresh })
  });

  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};
```

## Tests

Les tests complets sont disponibles dans `tests.py` et couvrent:
- Inscription et vérification d'email
- Connexion/déconnexion
- Réinitialisation de mot de passe
- Rate limiting
- Protection contre brute force
- Rotation de tokens

## Support

Pour toute question ou problème, consultez la documentation API complète à `/api/docs/` ou contactez l'équipe de développement.
