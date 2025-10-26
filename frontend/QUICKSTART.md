# 🚀 Quick Start Guide - 5 Minutes

Guide ultra-rapide pour mettre le frontend en ligne.

## Étape 1 : Configuration (2 min)

### Éditer `config.js`

```javascript
// Ligne 16 : Remplacer par votre URL Cloud Run
API_BASE_URL: 'https://VOTRE-URL-CLOUD-RUN',

// Lignes 24-26 : Vos liens
SOCIAL_LINKS: {
    github: 'https://github.com/VOTRE-USERNAME/constellation-tech',
    linkedin: 'https://linkedin.com/in/VOTRE-PROFIL',
},
```

**Où trouver l'URL Cloud Run ?**
- Backend déployé → Cloud Run Console → URL du service
- Format : `https://constellation-tech-XXXXX-uc.a.run.app`

---

## Étape 2 : Assets (2 min)

### Option Rapide - Utiliser les Placeholders

Le site fonctionnera **sans** générer les assets. Les fallbacks sont en place :
- ✅ Favicons : SVG fourni (compatible navigateurs modernes)
- ✅ Background hero : Gradient CSS automatique
- ⚠️ OG Image : À créer pour le partage LinkedIn/Twitter

### Option Complète - Générer les Assets

```bash
cd assets/

# 1. Favicons (avec ImageMagick ou en ligne sur favicon.io)
convert favicon.svg -resize 180x180 apple-touch-icon.png
convert apple-touch-icon.png -resize 32x32 favicon-32x32.png
convert apple-touch-icon.png -resize 16x16 favicon-16x16.png

# 2. Background Hero (télécharger sur Unsplash)
# → https://unsplash.com/s/photos/constellation
# → Renommer en "constellation-hero-bg.png"

# 3. OG Image (créer sur Canva 1200x630)
# → Template simple avec le titre du projet
```

---

## Étape 3 : Test Local (30 sec)

```bash
# Dans le dossier frontend/
python3 -m http.server 8080

# Ouvrir dans le navigateur
open http://localhost:8080
```

**Vérifier** :
- ✅ Page s'affiche
- ✅ Particules spatiales animées
- ✅ Bouton "Choisir mon CV" réactif
- ⚠️ Upload → vérifier que l'API backend est accessible

---

## Étape 4 : Déploiement GitHub Pages (30 sec)

```bash
# 1. Push sur GitHub
git add .
git commit -m "Frontend: Initial deployment"
git push origin main

# 2. Activer GitHub Pages
# → GitHub.com → Votre repo → Settings → Pages
# → Source: main branch → /frontend folder → Save

# 3. Attendre 1-2 minutes, puis accéder à :
# https://VOTRE-USERNAME.github.io/constellation-tech/
```

---

## Étape 5 : Mise à jour des URLs OG (30 sec)

Dans `index.html`, lignes 17-19 et 22-25, remplacer :

```html
<meta property="og:url" content="https://VOTRE-USERNAME.github.io/constellation-tech/">
<meta property="og:image" content="https://VOTRE-USERNAME.github.io/constellation-tech/assets/og-image.png">

<meta property="twitter:url" content="https://VOTRE-USERNAME.github.io/constellation-tech/">
<meta property="twitter:image" content="https://VOTRE-USERNAME.github.io/constellation-tech/assets/og-image.png">
```

Push les changements :
```bash
git commit -am "Update OG meta tags"
git push
```

---

## ✅ Checklist de Validation

- [ ] `config.js` configuré (API_URL + liens sociaux)
- [ ] Test local fonctionne (`python3 -m http.server`)
- [ ] GitHub Pages activé
- [ ] Site accessible en ligne
- [ ] Upload CV → Loading → Résultat (avec backend fonctionnel)
- [ ] Responsive : tester sur mobile

---

## 🐛 Problèmes Fréquents

### "Failed to fetch" lors de l'upload

**Cause** : Backend non accessible ou CORS

**Solution** :
1. Vérifier l'URL dans `config.js`
2. Tester l'API :
   ```bash
   curl https://VOTRE-URL-CLOUD-RUN/api/generate-constellation
   ```
3. Vérifier CORS dans le backend (voir README backend)

### Particules ne s'affichent pas

**Solution** : Ouvrir console (F12), vérifier les erreurs.
Désactiver temporairement dans `config.js` :
```javascript
particlesEnabled: false
```

### Background hero manquant

**Normal** : Un gradient CSS est utilisé par défaut.
Pour ajouter une image, voir `assets/ASSETS.md`.

---

## 📖 Pour Aller Plus Loin

- **README.md** : Documentation complète
- **FRONTEND_BRIEF.md** : Spécifications détaillées
- **assets/ASSETS.md** : Guide complet des assets

---

**🎉 C'est tout ! Votre landing page est en ligne.**

**Test final** : Uploadez votre propre CV et partagez votre constellation sur LinkedIn ! 🌟
