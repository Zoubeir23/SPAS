# Logo ISI

Ce dossier contient le logo officiel de l'Institut Supérieur d'Informatique (ISI).

## Fichier requis

Placez le logo officiel de l'ISI dans ce dossier avec le nom suivant :

- **`isi-logo.png`** - Logo principal (format PNG recommandé)

## Formats acceptés

Le logo peut être au format :
- PNG (recommandé pour la transparence)
- SVG (pour une meilleure qualité à toutes les tailles)
- JPG/JPEG (si nécessaire)

## Emplacements d'utilisation

Le logo est utilisé dans :
- Page de connexion (`/login`)
- Page de mot de passe oublié (`/forgot-password`)
- Sidebar (barre latérale de navigation)
- Autres composants utilisant le composant `<Logo />`

## Composant Logo

Le composant `Logo` se trouve dans `src/components/common/Logo.tsx` et supporte plusieurs variantes :
- `default` : Logo seul
- `compact` : Logo avec texte à côté
- `full` : Logo avec texte en dessous

## Note

Si le fichier logo n'est pas trouvé, un fallback avec les initiales "ISI" sera affiché automatiquement.

