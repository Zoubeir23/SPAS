# Guide Intégration Frontend React - Backend Django

Ce guide explique comment connecter le frontend React (localhost:5173) au backend Django (localhost:8000).

---

## Configuration Backend pour Frontend

### 1. CORS Configuration

Le backend est déjà configuré pour accepter les requêtes du frontend React:

**Fichier**: `C:\Users\Public\Libraries\one\SPAS\backend\config\settings.py`

```python
# CORS Configuration (lignes 143-148)
CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=['http://localhost:5173', 'http://127.0.0.1:5173']
)
CORS_ALLOW_CREDENTIALS = True
```

**Fichier .env**:
```bash
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 2. URLs API Disponibles

**Base URL Backend**: `http://localhost:8000`

Tous les endpoints API sont préfixés par `/api/`:
- Authentification: `/api/auth/`
- Étudiants: `/api/students/`
- Programmes: `/api/programs/`
- Notes: `/api/grades/`
- Présences: `/api/attendance/`
- Prédictions: `/api/predictions/`
- Alertes: `/api/alerts/`
- etc.

---

## Authentification JWT

### 1. Flux Authentification

```
1. Login: POST /api/auth/token/
   → Retourne { access: "...", refresh: "..." }

2. Requêtes API: Header Authorization: Bearer <access_token>

3. Refresh token: POST /api/auth/token/refresh/
   → Retourne nouveau { access: "..." }

4. Verify token: POST /api/auth/token/verify/
   → Valide si token est encore valide
```

### 2. Code Frontend - Service Auth

**Fichier**: `frontend/src/services/api.ts` (à créer/adapter)

```typescript
// Configuration Axios
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important pour CORS avec credentials
});

// Intercepteur pour ajouter token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur pour refresh token automatique
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si erreur 401 et pas déjà retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          `${API_BASE_URL}/auth/token/refresh/`,
          { refresh: refreshToken }
        );

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        // Retry requête originale avec nouveau token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed → logout
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

### 3. Service Authentification

**Fichier**: `frontend/src/services/authService.ts`

```typescript
import api from './api';

interface LoginCredentials {
  email: string;
  password: string;
}

interface LoginResponse {
  access: string;
  refresh: string;
}

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: 'ADMIN' | 'TEACHER' | 'ADVISOR' | 'COORDINATOR';
}

export const authService = {
  // Login
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>(
      '/auth/token/',
      credentials
    );

    const { access, refresh } = response.data;

    // Stocker tokens
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);

    return response.data;
  },

  // Logout
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  // Get current user
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/users/me/');
    return response.data;
  },

  // Check if authenticated
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  // Verify token
  async verifyToken(): Promise<boolean> {
    try {
      const token = localStorage.getItem('access_token');
      await api.post('/auth/token/verify/', { token });
      return true;
    } catch {
      return false;
    }
  },
};
```

### 4. Exemple Login Component

```typescript
import { useState } from 'react';
import { authService } from '@/services/authService';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authService.login({ email, password });

      // Récupérer infos utilisateur
      const user = await authService.getCurrentUser();
      console.log('Logged in as:', user);

      // Rediriger vers dashboard
      navigate('/dashboard');
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
        'Email ou mot de passe incorrect'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Mot de passe"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Connexion...' : 'Se connecter'}
      </button>
      {error && <div className="error">{error}</div>}
    </form>
  );
}
```

---

## Services API Frontend

### 1. Students Service

**Fichier**: `frontend/src/services/studentsService.ts`

```typescript
import api from './api';

export interface Student {
  id: number;
  matricule: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  date_of_birth: string;
  program: number;
  program_name?: string;
  session: number;
  session_name?: string;
  status: 'active' | 'inactive' | 'graduated';
  risk_level?: 'low' | 'medium' | 'high';
  risk_score?: number;
  created_at: string;
  updated_at: string;
}

export interface StudentListParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: string;
  program?: number;
  risk_level?: string;
}

export const studentsService = {
  // Liste étudiants avec filtres
  async getStudents(params?: StudentListParams) {
    const response = await api.get<{
      count: number;
      next: string | null;
      previous: string | null;
      results: Student[];
    }>('/students/', { params });
    return response.data;
  },

  // Détails étudiant
  async getStudent(id: number) {
    const response = await api.get<Student>(`/students/${id}/`);
    return response.data;
  },

  // Créer étudiant
  async createStudent(data: Partial<Student>) {
    const response = await api.post<Student>('/students/', data);
    return response.data;
  },

  // Modifier étudiant
  async updateStudent(id: number, data: Partial<Student>) {
    const response = await api.put<Student>(`/students/${id}/`, data);
    return response.data;
  },

  // Supprimer étudiant
  async deleteStudent(id: number) {
    await api.delete(`/students/${id}/`);
  },

  // Étudiants à risque
  async getAtRiskStudents() {
    const response = await api.get<Student[]>('/students/at_risk/');
    return response.data;
  },
};
```

### 2. Alerts Service

```typescript
import api from './api';

export interface Alert {
  id: number;
  student: number;
  student_name?: string;
  alert_type: 'DROPOUT_RISK' | 'LOW_GRADES' | 'LOW_ATTENDANCE' | 'BEHAVIORAL';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED' | 'DISMISSED';
  title: string;
  description: string;
  assigned_to?: number;
  assigned_to_name?: string;
  created_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
}

export const alertsService = {
  // Toutes les alertes
  async getAlerts(params?: {
    status?: string;
    severity?: string;
    alert_type?: string;
  }) {
    const response = await api.get<{ results: Alert[] }>('/alerts/alerts/', {
      params
    });
    return response.data;
  },

  // Mes alertes
  async getMyAlerts() {
    const response = await api.get<Alert[]>('/alerts/alerts/my_alerts/');
    return response.data;
  },

  // Alertes critiques
  async getCriticalAlerts() {
    const response = await api.get<Alert[]>('/alerts/alerts/critical/');
    return response.data;
  },

  // Accuser réception
  async acknowledgeAlert(id: number) {
    const response = await api.post<Alert>(
      `/alerts/alerts/${id}/acknowledge/`
    );
    return response.data;
  },

  // Résoudre alerte
  async resolveAlert(id: number, data: { resolution_notes: string }) {
    const response = await api.post<Alert>(
      `/alerts/alerts/${id}/resolve/`,
      data
    );
    return response.data;
  },

  // Assigner alerte
  async assignAlert(id: number, userId: number) {
    const response = await api.post<Alert>(
      `/alerts/alerts/${id}/assign/`,
      { user_id: userId }
    );
    return response.data;
  },
};
```

### 3. Predictions Service

```typescript
import api from './api';

export interface Prediction {
  id: number;
  student: number;
  student_name?: string;
  model: number;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence: number;
  contributing_factors: Record<string, any>;
  created_at: string;
}

export const predictionsService = {
  // Toutes les prédictions
  async getPredictions(params?: { student?: number }) {
    const response = await api.get<{ results: Prediction[] }>(
      '/predictions/predictions/',
      { params }
    );
    return response.data;
  },

  // Étudiants à risque (prédictions HIGH/CRITICAL)
  async getAtRiskPredictions() {
    const response = await api.get<Prediction[]>(
      '/predictions/predictions/at_risk/'
    );
    return response.data;
  },

  // Statistiques prédictions
  async getStatistics() {
    const response = await api.get<{
      total_predictions: number;
      risk_distribution: Record<string, number>;
      // ...
    }>('/predictions/predictions/statistics/');
    return response.data;
  },

  // Générer prédictions en masse (async)
  async generateBulkPredictions(periodId?: number) {
    const response = await api.post<{ task_id: string }>(
      '/predictions/predictions/generate_bulk/',
      { period_id: periodId }
    );
    return response.data;
  },
};
```

### 4. Grades Service

```typescript
import api from './api';

export interface Grade {
  id: number;
  student: number;
  course_session: number;
  evaluation_name: string;
  score: number;
  weight: number;
  date: string;
  weighted_grade: number;
}

export interface CourseGradeSummary {
  id: number;
  student: number;
  student_name?: string;
  course_session: number;
  course_name?: string;
  final_score: number;
  letter_grade: string;
  gpa: number;
  is_passing: boolean;
}

export const gradesService = {
  // Notes
  async getGrades(params?: { student?: number; course_session?: number }) {
    const response = await api.get<{ results: Grade[] }>('/grades/grades/', {
      params
    });
    return response.data;
  },

  // Créer note
  async createGrade(data: Partial<Grade>) {
    const response = await api.post<Grade>('/grades/grades/', data);
    return response.data;
  },

  // Résumés notes
  async getGradeSummaries(params?: { student?: number }) {
    const response = await api.get<{ results: CourseGradeSummary[] }>(
      '/grades/summaries/',
      { params }
    );
    return response.data;
  },

  // Étudiants en échec
  async getFailingStudents() {
    const response = await api.get<CourseGradeSummary[]>(
      '/grades/summaries/failing_students/'
    );
    return response.data;
  },
};
```

### 5. Attendance Service

```typescript
import api from './api';

export interface AttendanceRecord {
  id: number;
  student: number;
  course_session: number;
  date: string;
  status: 'PRESENT' | 'ABSENT' | 'LATE' | 'EXCUSED';
  notes?: string;
}

export interface AttendanceSummary {
  id: number;
  student: number;
  student_name?: string;
  course_session: number;
  course_name?: string;
  total_classes: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  excused_count: number;
  attendance_rate: number;
}

export const attendanceService = {
  // Enregistrements
  async getRecords(params?: {
    student?: number;
    course_session?: number;
    date?: string;
  }) {
    const response = await api.get<{ results: AttendanceRecord[] }>(
      '/attendance/records/',
      { params }
    );
    return response.data;
  },

  // Créer enregistrement
  async createRecord(data: Partial<AttendanceRecord>) {
    const response = await api.post<AttendanceRecord>(
      '/attendance/records/',
      data
    );
    return response.data;
  },

  // Création en masse
  async bulkCreateRecords(records: Partial<AttendanceRecord>[]) {
    const response = await api.post<AttendanceRecord[]>(
      '/attendance/records/bulk_create/',
      { records }
    );
    return response.data;
  },

  // Résumés
  async getSummaries(params?: { student?: number }) {
    const response = await api.get<{ results: AttendanceSummary[] }>(
      '/attendance/summaries/',
      { params }
    );
    return response.data;
  },

  // Faible présence
  async getLowAttendance() {
    const response = await api.get<AttendanceSummary[]>(
      '/attendance/summaries/low_attendance/'
    );
    return response.data;
  },
};
```

---

## Composants React - Exemples

### 1. Liste Étudiants

```typescript
import { useEffect, useState } from 'react';
import { studentsService, Student } from '@/services/studentsService';

export default function StudentsList() {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    risk_level: '',
  });

  useEffect(() => {
    loadStudents();
  }, [filters]);

  const loadStudents = async () => {
    setLoading(true);
    try {
      const data = await studentsService.getStudents(filters);
      setStudents(data.results);
    } catch (error) {
      console.error('Erreur chargement étudiants:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Chargement...</div>;

  return (
    <div>
      {/* Filtres */}
      <div className="filters">
        <input
          type="text"
          placeholder="Rechercher..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
        />
        <select
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}
        >
          <option value="">Tous statuts</option>
          <option value="active">Actif</option>
          <option value="inactive">Inactif</option>
          <option value="graduated">Diplômé</option>
        </select>
        <select
          value={filters.risk_level}
          onChange={(e) => setFilters({ ...filters, risk_level: e.target.value })}
        >
          <option value="">Tous niveaux de risque</option>
          <option value="low">Faible</option>
          <option value="medium">Moyen</option>
          <option value="high">Élevé</option>
        </select>
      </div>

      {/* Liste */}
      <table>
        <thead>
          <tr>
            <th>Matricule</th>
            <th>Nom</th>
            <th>Email</th>
            <th>Programme</th>
            <th>Statut</th>
            <th>Risque</th>
          </tr>
        </thead>
        <tbody>
          {students.map((student) => (
            <tr key={student.id}>
              <td>{student.matricule}</td>
              <td>{student.first_name} {student.last_name}</td>
              <td>{student.email}</td>
              <td>{student.program_name}</td>
              <td>{student.status}</td>
              <td>
                <span className={`risk-${student.risk_level}`}>
                  {student.risk_level} ({student.risk_score})
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### 2. Dashboard Alertes

```typescript
import { useEffect, useState } from 'react';
import { alertsService, Alert } from '@/services/alertsService';

export default function AlertsDashboard() {
  const [criticalAlerts, setCriticalAlerts] = useState<Alert[]>([]);
  const [myAlerts, setMyAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      const [critical, my] = await Promise.all([
        alertsService.getCriticalAlerts(),
        alertsService.getMyAlerts(),
      ]);
      setCriticalAlerts(critical);
      setMyAlerts(my);
    } catch (error) {
      console.error('Erreur chargement alertes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async (id: number) => {
    try {
      await alertsService.acknowledgeAlert(id);
      loadAlerts(); // Recharger
    } catch (error) {
      console.error('Erreur accusé réception:', error);
    }
  };

  const handleResolve = async (id: number) => {
    const notes = prompt('Notes de résolution:');
    if (!notes) return;

    try {
      await alertsService.resolveAlert(id, { resolution_notes: notes });
      loadAlerts();
    } catch (error) {
      console.error('Erreur résolution:', error);
    }
  };

  if (loading) return <div>Chargement...</div>;

  return (
    <div>
      <h2>Alertes Critiques ({criticalAlerts.length})</h2>
      <div className="alerts-list">
        {criticalAlerts.map((alert) => (
          <div key={alert.id} className="alert-card critical">
            <h3>{alert.title}</h3>
            <p>{alert.description}</p>
            <p>Étudiant: {alert.student_name}</p>
            <p>Type: {alert.alert_type}</p>
            <div className="actions">
              {alert.status === 'ACTIVE' && (
                <button onClick={() => handleAcknowledge(alert.id)}>
                  Accuser réception
                </button>
              )}
              {alert.status === 'ACKNOWLEDGED' && (
                <button onClick={() => handleResolve(alert.id)}>
                  Résoudre
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      <h2>Mes Alertes ({myAlerts.length})</h2>
      {/* Similar list */}
    </div>
  );
}
```

---

## Gestion Erreurs API

### 1. Wrapper Service avec Gestion Erreurs

```typescript
// utils/apiWrapper.ts
export async function apiCall<T>(
  fn: () => Promise<T>,
  errorMessage = 'Une erreur est survenue'
): Promise<T | null> {
  try {
    return await fn();
  } catch (error: any) {
    console.error(errorMessage, error);

    // Afficher erreur utilisateur
    if (error.response?.data?.error?.message) {
      alert(error.response.data.error.message);
    } else {
      alert(errorMessage);
    }

    return null;
  }
}

// Utilisation
import { apiCall } from '@/utils/apiWrapper';

const students = await apiCall(
  () => studentsService.getStudents(),
  'Erreur chargement étudiants'
);

if (students) {
  setStudents(students.results);
}
```

### 2. Format Erreur Backend

Le backend retourne des erreurs au format:

```json
{
  "success": false,
  "error": {
    "message": "Message d'erreur principal",
    "status_code": 400,
    "details": {
      "field1": ["Erreur validation field1"],
      "field2": ["Erreur validation field2"]
    }
  }
}
```

---

## WebSocket / Real-time (Optionnel)

Pour les notifications temps réel, utiliser Django Channels (à implémenter):

```typescript
// websocketService.ts
const ws = new WebSocket('ws://localhost:8000/ws/notifications/');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Nouvelle notification:', data);

  // Afficher notification
  showNotification(data.message);

  // Recharger alertes si nécessaire
  if (data.type === 'new_alert') {
    reloadAlerts();
  }
};
```

---

## Checklist Intégration

### Backend
- [x] CORS configuré pour localhost:5173
- [x] JWT configuré (access + refresh tokens)
- [x] Tous endpoints API fonctionnels
- [x] Documentation API disponible (Swagger)
- [ ] WebSocket pour notifications temps réel (optionnel)

### Frontend
- [ ] Service API configuré avec Axios
- [ ] Intercepteurs JWT (request + response)
- [ ] Service authentification (login, logout, getCurrentUser)
- [ ] Services pour chaque module (students, alerts, predictions, etc.)
- [ ] Gestion erreurs API
- [ ] Protected routes (redirection si non authentifié)
- [ ] Stockage tokens sécurisé (localStorage ou cookies)
- [ ] Refresh token automatique
- [ ] Logout automatique si token invalide

---

## Démarrage Rapide

### 1. Démarrer Backend

```bash
cd C:\Users\Public\Libraries\one\SPAS\backend

# Activer environnement virtuel
venv\Scripts\activate

# Démarrer serveur
python manage.py runserver
```

**Backend disponible**: http://localhost:8000

### 2. Démarrer Frontend

```bash
cd C:\Users\Public\Libraries\one\SPAS\frontend

# Installer dépendances (si pas fait)
npm install axios

# Démarrer dev server
npm run dev
```

**Frontend disponible**: http://localhost:5173

### 3. Tester Connexion

1. Ouvrir http://localhost:5173
2. Page login doit apparaître
3. Entrer credentials (créés via `createsuperuser`)
4. Après login, redirection vers dashboard
5. Vérifier dans DevTools Network que requêtes API fonctionnent

---

## Troubleshooting

### Erreur CORS

**Symptôme**: `Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:5173' has been blocked by CORS policy`

**Solution**:
1. Vérifier `CORS_ALLOWED_ORIGINS` dans `settings.py`
2. Vérifier `.env` contient `CORS_ALLOWED_ORIGINS=http://localhost:5173`
3. Redémarrer serveur Django

### Token Expiré

**Symptôme**: Erreur 401 après quelques minutes

**Solution**: Vérifier que intercepteur Axios refresh automatiquement le token

### Connexion Refusée

**Symptôme**: `Network Error` ou `ERR_CONNECTION_REFUSED`

**Solution**: Vérifier que backend Django est démarré sur port 8000

### Données Non Affichées

**Symptôme**: Liste vide alors que données existent

**Solution**:
1. Vérifier dans Network DevTools que requête retourne données
2. Vérifier format réponse (paginé: `{ count, next, previous, results }`)
3. Vérifier que `results` est bien utilisé: `data.results`

---

**Dernière mise à jour**: 2026-01-02
**Version**: 1.0.0
