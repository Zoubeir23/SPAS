# Script final pour mettre à jour tous les imports restants

$files = Get-ChildItem -Path "src" -Recurse -Filter "*.tsx" | Where-Object { $_.FullName -notmatch "node_modules" }

$replacements = @{
    # Composants communs
    "import Input from '@/components/common/Input'" = "import ChampSaisie from '@/components/common/ChampSaisie'"
    "import Button from '@/components/common/Button'" = "import Bouton from '@/components/common/Bouton'"
    "import Card from '@/components/common/Card'" = "import Carte from '@/components/common/Carte'"
    "import Alert from '@/components/common/Alert'" = "import Alerte from '@/components/common/Alerte'"
    "import Checkbox from '@/components/common/Checkbox'" = "import CaseCochee from '@/components/common/CaseCochee'"
    "import DataTable from '@/components/common/DataTable'" = "import TableauDonnees from '@/components/common/TableauDonnees'"
    "import LoadingSpinner from '@/components/common/LoadingSpinner'" = "import IndicateurChargement from '@/components/common/IndicateurChargement'"
    "import SearchBar from '@/components/common/SearchBar'" = "import BarreRecherche from '@/components/common/BarreRecherche'"
    "import Breadcrumbs from '@/components/common/Breadcrumbs'" = "import FilDAriane from '@/components/common/FilDAriane'"
    
    # Modales
    "import Modal from '@/components/modals/Modal'" = "import Modale from '@/components/modals/Modale'"
    "import StudentModal from '@/components/modals/StudentModal'" = "import ModaleEtudiant from '@/components/modals/ModaleEtudiant'"
    "import InterventionModal from '@/components/modals/InterventionModal'" = "import ModaleIntervention from '@/components/modals/ModaleIntervention'"
    "import TrainingModal from '@/components/modals/TrainingModal'" = "import ModaleEntrainement from '@/components/modals/ModaleEntrainement'"
    "import UserModal from '@/components/modals/UserModal'" = "import ModaleUtilisateur from '@/components/modals/ModaleUtilisateur'"
    
    # Graphiques
    "import BarChart from '@/components/charts/BarChart'" = "import GraphiqueBarres from '@/components/charts/GraphiqueBarres'"
    "import LineChart from '@/components/charts/LineChart'" = "import GraphiqueLignes from '@/components/charts/GraphiqueLignes'"
    "import PieChart from '@/components/charts/PieChart'" = "import GraphiqueCirculaire from '@/components/charts/GraphiqueCirculaire'"
    "import GaugeChart from '@/components/charts/GaugeChart'" = "import GraphiqueJauge from '@/components/charts/GraphiqueJauge'"
}

$jsxReplacements = @{
    "<Input" = "<ChampSaisie"
    "</Input>" = "</ChampSaisie>"
    "<Button" = "<Bouton"
    "</Button>" = "</Bouton>"
    "<Card" = "<Carte"
    "</Card>" = "</Carte>"
    "<Alert" = "<Alerte"
    "</Alert>" = "</Alerte>"
    "<Checkbox" = "<CaseCochee"
    "</Checkbox>" = "</CaseCochee>"
    "<DataTable" = "<TableauDonnees"
    "</DataTable>" = "</TableauDonnees>"
    "<LoadingSpinner" = "<IndicateurChargement"
    "</LoadingSpinner>" = "</IndicateurChargement>"
    "<SearchBar" = "<BarreRecherche"
    "</SearchBar>" = "</BarreRecherche>"
    "<Breadcrumbs" = "<FilDAriane"
    "</Breadcrumbs>" = "</FilDAriane>"
    "<Modal" = "<Modale"
    "</Modal>" = "</Modale>"
    "<StudentModal" = "<ModaleEtudiant"
    "</StudentModal>" = "</ModaleEtudiant>"
    "<InterventionModal" = "<ModaleIntervention"
    "</InterventionModal>" = "</ModaleIntervention>"
    "<TrainingModal" = "<ModaleEntrainement"
    "</TrainingModal>" = "</ModaleEntrainement>"
    "<UserModal" = "<ModaleUtilisateur"
    "</UserModal>" = "</ModaleUtilisateur>"
    "<BarChart" = "<GraphiqueBarres"
    "</BarChart>" = "</GraphiqueBarres>"
    "<LineChart" = "<GraphiqueLignes"
    "</LineChart>" = "</GraphiqueLignes>"
    "<PieChart" = "<GraphiqueCirculaire"
    "</PieChart>" = "</GraphiqueCirculaire>"
    "<GaugeChart" = "<GraphiqueJauge"
    "</GaugeChart>" = "</GraphiqueJauge>"
}

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $updated = $content
    
    # Remplacer les imports
    foreach ($key in $replacements.Keys) {
        $updated = $updated -replace [regex]::Escape($key), $replacements[$key]
    }
    
    # Remplacer les utilisations JSX
    foreach ($key in $jsxReplacements.Keys) {
        $updated = $updated -replace [regex]::Escape($key), $jsxReplacements[$key]
    }
    
    if ($content -ne $updated) {
        Set-Content -Path $file.FullName -Value $updated -NoNewline
        Write-Host "Mis à jour: $($file.Name)" -ForegroundColor Green
    }
}

Write-Host "`nTerminé!" -ForegroundColor Cyan

