# Script PowerShell pour renommer tous les fichiers en français

Write-Host "=== RENOMMAGE DES FICHIERS EN FRANÇAIS ===" -ForegroundColor Cyan

# Pages - Authentification
Write-Host "Renommage des pages d'authentification..." -ForegroundColor Yellow
# Déjà fait: Login.tsx -> Connexion.tsx
# Déjà fait: ForgotPassword.tsx -> MotDePasseOublie.tsx

# Pages - Dashboards
Write-Host "Renommage des dashboards..." -ForegroundColor Yellow
Move-Item -Path "src/pages/dashboard/GeneralDashboard.tsx" -Destination "src/pages/dashboard/TableauDeBordGeneral.tsx" -ErrorAction SilentlyContinue
Move-Item -Path "src/pages/dashboard/PredictiveDashboard.tsx" -Destination "src/pages/dashboard/TableauDeBordPredictif.tsx" -ErrorAction SilentlyContinue
Move-Item -Path "src/pages/analytics/AdvancedAnalytics.tsx" -Destination "src/pages/analytics/AnalysesAvancees.tsx" -ErrorAction SilentlyContinue

# Pages - Étudiants
Write-Host "Renommage des pages étudiants..." -ForegroundColor Yellow
Move-Item -Path "src/pages/students/StudentList.tsx" -Destination "src/pages/students/ListeEtudiants.tsx" -ErrorAction SilentlyContinue
Move-Item -Path "src/pages/students/StudentDetail.tsx" -Destination "src/pages/students/DetailEtudiant.tsx" -ErrorAction SilentlyContinue

# Pages - Académique
Write-Host "Renommage des pages académiques..." -ForegroundColor Yellow
Move-Item -Path "src/pages/sessions/SessionList.tsx" -Destination "src/pages/sessions/ListeSessions.tsx" -ErrorAction SilentlyContinue
Move-Item -Path "src/pages/programs/ProgramList.tsx" -Destination "src/pages/programs/ListeFilieres.tsx" -ErrorAction SilentlyContinue
Move-Item -Path "src/pages/attendance/AttendanceManagement.tsx" -Destination "src/pages/attendance/GestionAbsences.tsx" -ErrorAction SilentlyContinue
Move-Item -Path "src/pages/grades/GradeEntry.tsx" -Destination "src/pages/grades/SaisieNotes.tsx" -ErrorAction SilentlyContinue

# Pages - IA/Prédictions
Write-Host "Renommage des pages IA..." -ForegroundColor Yellow
Move-Item -Path "src/pages/predictions/PredictionDetail.tsx" -Destination "src/pages/predictions/DetailPrediction.tsx" -ErrorAction SilentlyContinue
Move-Item -Path "src/pages/alerts/AlertList.tsx" -Destination "src/pages/alerts/ListeAlertes.tsx" -ErrorAction SilentlyContinue
Move-Item -Path "src/pages/ml/ModelManagement.tsx" -Destination "src/pages/ml/GestionModeles.tsx" -ErrorAction SilentlyContinue
Move-Item -Path "src/pages/ml/ModelDetails.tsx" -Destination "src/pages/ml/DetailModele.tsx" -ErrorAction SilentlyContinue

# Pages - Administration
Write-Host "Renommage des pages administration..." -ForegroundColor Yellow
Move-Item -Path "src/pages/users/UserManagement.tsx" -Destination "src/pages/users/GestionUtilisateurs.tsx" -ErrorAction SilentlyContinue
Move-Item -Path "src/pages/settings/SystemSettings.tsx" -Destination "src/pages/settings/ParametresSysteme.tsx" -ErrorAction SilentlyContinue
Move-Item -Path "src/pages/NotFound.tsx" -Destination "src/pages/PageNonTrouvee.tsx" -ErrorAction SilentlyContinue

Write-Host "`n=== RENOMMAGE TERMINÉ ===" -ForegroundColor Green
Write-Host "ATTENTION: Il faut maintenant mettre à jour tous les imports!" -ForegroundColor Red

