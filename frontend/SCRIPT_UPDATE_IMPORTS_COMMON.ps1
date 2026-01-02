# Script pour mettre à jour tous les imports des composants communs

$replacements = @{
    "import Input from '@/components/common/Input'" = "import ChampSaisie from '@/components/common/ChampSaisie'"
    "import Button from '@/components/common/Button'" = "import Bouton from '@/components/common/Bouton'"
    "import Card from '@/components/common/Card'" = "import Carte from '@/components/common/Carte'"
    "import Alert from '@/components/common/Alert'" = "import Alerte from '@/components/common/Alerte'"
    "import Checkbox from '@/components/common/Checkbox'" = "import CaseCochee from '@/components/common/CaseCochee'"
    "import DataTable from '@/components/common/DataTable'" = "import TableauDonnees from '@/components/common/TableauDonnees'"
    "import LoadingSpinner from '@/components/common/LoadingSpinner'" = "import IndicateurChargement from '@/components/common/IndicateurChargement'"
    "import SearchBar from '@/components/common/SearchBar'" = "import BarreRecherche from '@/components/common/BarreRecherche'"
    "import Breadcrumbs from '@/components/common/Breadcrumbs'" = "import FilDAriane from '@/components/common/FilDAriane'"
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
}

$files = Get-ChildItem -Path "src" -Recurse -Filter "*.tsx" | Where-Object { $_.FullName -notmatch "node_modules" }

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

