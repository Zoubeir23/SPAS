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
          <RouteProtegee>
            <TableauDeBordGeneral />
          </RouteProtegee>
        }
      />
      <Route
        path={ROUTES.DASHBOARD_PREDICTIVE}
        element={
          <RouteProtegee>
            <TableauDeBordPredictif />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Étudiants */}
      <Route
        path={ROUTES.STUDENTS}
        element={
          <RouteProtegee>
            <ListeEtudiants />
          </RouteProtegee>
        }
      />
      <Route
        path="/students/:id"
        element={
          <RouteProtegee>
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

      {/* Routes protégées - Prédictions */}
      <Route
        path={ROUTES.PREDICTIONS}
        element={
          <RouteProtegee>
            <ListePredictions />
          </RouteProtegee>
        }
      />
      <Route
        path="/predictions/:id"
        element={
          <RouteProtegee>
            <DetailPrediction />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Utilisateurs */}
      <Route
        path={ROUTES.USERS}
        element={
          <RouteProtegee>
            <GestionUtilisateurs />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - ML */}
      <Route
        path={ROUTES.ML_MODELS}
        element={
          <RouteProtegee>
            <GestionModeles />
          </RouteProtegee>
        }
      />
      <Route
        path="/ml/models/:id"
        element={
          <RouteProtegee>
            <DetailModele />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Absences */}
      <Route
        path={ROUTES.ATTENDANCE}
        element={
          <RouteProtegee>
            <GestionAbsences />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Notes */}
      <Route
        path={ROUTES.GRADES}
        element={
          <RouteProtegee>
            <SaisieNotes />
          </RouteProtegee>
        }
      />

      {/* Routes protégées - Paramètres */}
      <Route
        path={ROUTES.SETTINGS}
        element={
          <RouteProtegee>
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

      {/* Routes protégées - Analytics */}
      <Route
        path={ROUTES.ANALYTICS}
        element={
          <RouteProtegee>
            <AnalysesAvancees />
          </RouteProtegee>
        }
      />

      {/* Route 404 */}
      <Route path="*" element={<PageNonTrouvee />} />
    </Routes>
  )
}
