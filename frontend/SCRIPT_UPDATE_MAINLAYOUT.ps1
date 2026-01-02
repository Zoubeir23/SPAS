# Script pour mettre à jour tous les MainLayout en MiseEnPagePrincipale

$files = Get-ChildItem -Path "src/pages" -Recurse -Filter "*.tsx"

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $updated = $content -replace "import MainLayout from '@/components/layout/MainLayout'", "import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'"
    $updated = $updated -replace "<MainLayout", "<MiseEnPagePrincipale"
    $updated = $updated -replace "</MainLayout>", "</MiseEnPagePrincipale>"
    
    if ($content -ne $updated) {
        Set-Content -Path $file.FullName -Value $updated -NoNewline
        Write-Host "Mis à jour: $($file.FullName)" -ForegroundColor Green
    }
}

Write-Host "`nTerminé!" -ForegroundColor Cyan

