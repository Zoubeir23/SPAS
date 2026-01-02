# Instructions pour ajouter le logo officiel ISI

## 📋 Étapes à suivre

1. **Placez le fichier logo** dans ce dossier (`frontend/public/images/`) avec le nom exact :
   ```
   isi-logo.png
   ```

2. **Formats acceptés** :
   - PNG (recommandé pour la transparence)
   - SVG (pour une meilleure qualité vectorielle)
   - JPG/JPEG (si nécessaire)

3. **Taille recommandée** :
   - Minimum : 200x200 pixels
   - Optimal : 400x400 pixels ou plus
   - Format carré recommandé pour un meilleur rendu

## ✅ Vérification

Une fois le logo ajouté, il apparaîtra automatiquement dans :
- ✅ Page de connexion (`/login`)
- ✅ Page de mot de passe oublié (`/forgot-password`)
- ✅ Sidebar (barre latérale de navigation)
- ✅ Tous les composants utilisant `<Logo />`

## 🔄 Fallback

Si le logo n'est pas trouvé, un fallback avec les initiales "ISI" sera affiché automatiquement.

## 📝 Note

Le logo doit respecter les couleurs officielles de l'ISI :
- Bleu foncé pour le texte "GROUPE"
- Bleu avec dégradé pour les lettres "ISI"
- Texte "Institut Supérieur d'Informatique" en bleu foncé

