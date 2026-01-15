import { Routes, Route, Navigate } from 'react-router-dom'
import { ROUTES } from '@/utils/constants'
import RoutePublique from './RoutePublique'
import RouteProtegee from './RouteProtegee'
import Connexion from '@/pages/auth/Connexion'
import MotDePasseOublie from '@/pages/auth/MotDePasseOublie'
import PageNonTrouvee from '@/pages/PageNonTrouvee'

// Dashboards
import TableauDeBordGeneral from '@/pages/dashboard/TableauDeBordGeneral'
import TableauDeBordPredictif from '@/pages/dashboard/TableauDeBordPredictif'

// Lists
import ListeEtudiants from '@/pages/students/ListeEtudiants'
import ListeSessions from '@/pages/sessions/ListeSessions'
import ListeDepartements from '@/pages/programs/ListeDepartements'
import ListeFilieres from '@/pages/programs/ListeFilieres'
import ListeAlertes from '@/pages/alerts/ListeAlertes'

// Import pages
import DetailEtudiant from '@/pages/students/DetailEtudiant'
import ListePredictions from '@/pages/predictions/ListePredictions'
import DetailPrediction from '@/pages/predictions/DetailPrediction'
import GestionUtilisateurs from '@/pages/users/GestionUtilisateurs'
import GestionModeles from '@/pages/ml/GestionModeles'
import DetailModele from '@/pages/ml/DetailModele'
import GestionAbsences from '@/pages/attendance/GestionAbsences'
import SaisieNotes from '@/pages/grades/SaisieNotes'
import ParametresSysteme from '@/pages/settings/ParametresSysteme'
import MonProfil from '@/pages/profile/MonProfil'
import AnalysesAvancees from '@/pages/analytics/AnalysesAvancees'

export default function AppRoutes() {
  return (
    <Routes>
      {/* Route racine - redirige vers login si non connecté */}
      <Route
        path={ROUTES.HOME}
        element={
          <Navigate
            to={ROUTES.LOGIN}
            replace
          />
        }
      />

      {/* Routes publiques */}
      <Route
        path={ROUTES.LOGIN}
        element={
          <RoutePublique>
            <Connexion />
          </RoutePublique>
        }
      />
      <Route
        path={ROUTES.FORGOT_PASSWORD}
        element={
          <RoutePublique>
            <MotDePasseOublie />
          </RoutePublique>
        }
      />

      {/* Routes protégées - Dashboards */}
      <Route
        path={ROUTES.DASHBOARD}
        element={
          <RouteProtegee allowedRoles={['admin', 'teacher', 'pedagogical']}>
            <TableauDeBordGeneral />
          </RouteProtegee>
        }
      />
      <Route
        path={ROUTES.DASHBOARD_PREDICTIVE}
        element={
          <RouteProtegee allowedRoles={['admin', 'ds', 'pedagogical']}>
            <TableauDeBordPredictif />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Étudiants (pas pour DS) */}
      <Route
        path={ROUTES.STUDENTS}
        element={
          <RouteProtegee allowedRoles={['admin', 'teacher', 'pedagogical']}>
            <ListeEtudiants />
          </RouteProtegee>
        }
      />
      <Route
        path="/students/:id"
        element={
          <RouteProtegee allowedRoles={['admin', 'teacher', 'pedagogical']}>
            <DetailEtudiant />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Sessions */}
      <Route
        path={ROUTES.SESSIONS}
        element={
          <RouteProtegee>
            <ListeSessions />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Filières */}
      <Route
        path={ROUTES.PROGRAMS}
        element={
          <RouteProtegee>
            <ListeFilieres />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Départements */}
      <Route
        path="/departments"
        element={
          <RouteProtegee>
            <ListeDepartements />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Alertes */}
      <Route
        path={ROUTES.ALERTS}
        element={
          <RouteProtegee>
            <ListeAlertes />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Prédictions (admin, DS, pédagogique) */}
      <Route
        path={ROUTES.PREDICTIONS}
        element={
          <RouteProtegee allowedRoles={['admin', 'ds', 'pedagogical']}>
            <ListePredictions />
          </RouteProtegee>
        }
      />
      <Route
        path="/predictions/:id"
        element={
          <RouteProtegee allowedRoles={['admin', 'ds', 'pedagogical']}>
            <DetailPrediction />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Utilisateurs (admin uniquement) */}
      <Route
        path={ROUTES.USERS}
        element={
          <RouteProtegee allowedRoles={['admin']}>
            <GestionUtilisateurs />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - ML (admin et DS) */}
      <Route
        path={ROUTES.ML_MODELS}
        element={
          <RouteProtegee allowedRoles={['admin', 'ds']}>
            <GestionModeles />
          </RouteProtegee>
        }
      />
      <Route
        path="/ml/models/:id"
        element={
          <RouteProtegee allowedRoles={['admin', 'ds']}>
            <DetailModele />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Absences (pas pour DS) */}
      <Route
        path={ROUTES.ATTENDANCE}
        element={
          <RouteProtegee allowedRoles={['admin', 'teacher', 'pedagogical']}>
            <GestionAbsences />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Notes (pas pour DS) */}
      <Route
        path={ROUTES.GRADES}
        element={
          <RouteProtegee allowedRoles={['admin', 'teacher', 'pedagogical']}>
            <SaisieNotes />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Paramètres (admin uniquement) */}
      <Route
        path={ROUTES.SETTINGS}
        element={
          <RouteProtegee allowedRoles={['admin']}>
            <ParametresSysteme />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Profil */}
      <Route
        path={ROUTES.PROFILE}
        element={
          <RouteProtegee>
            <MonProfil />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Analytics (admin, DS, pédagogique) */}
      <Route
        path={ROUTES.ANALYTICS}
        element={
          <RouteProtegee allowedRoles={['admin', 'ds', 'pedagogical']}>
            <AnalysesAvancees />
          </RouteProtegee>
        }
      />

      {/* Route 404 */}
      <Route path="*" element={<PageNonTrouvee />} />
    </Routes>
  )
}
