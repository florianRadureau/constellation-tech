# Assets Guide - Constellation Tech

Ce dossier contient les assets graphiques du projet.

## 📋 Assets Requis

### 1. Favicons

Les favicons doivent être générés dans les tailles suivantes :

- **favicon-16x16.png** : 16x16px
- **favicon-32x32.png** : 32x32px
- **apple-touch-icon.png** : 180x180px

**Comment générer :**

1. Visitez [favicon.io](https://favicon.io/)
2. Choisissez "Text" ou "Image"
3. Options suggérées :
   - **Text** : "⭐" ou "CT"
   - **Font** : Space Mono
   - **Background** : #0A0A14 (dark blue)
   - **Color** : #6496FF (primary blue)
4. Téléchargez et extrayez dans ce dossier

**Alternative rapide avec ImageMagick :**
```bash
# Créer un favicon simple avec étoile
convert -size 180x180 xc:#0A0A14 \
  -font "Space-Mono" -pointsize 120 \
  -fill "#6496FF" -gravity center \
  -annotate +0+0 "⭐" \
  apple-touch-icon.png

# Redimensionner pour les autres tailles
convert apple-touch-icon.png -resize 32x32 favicon-32x32.png
convert apple-touch-icon.png -resize 16x16 favicon-16x16.png
```

---

### 2. Open Graph Image

**Fichier** : `og-image.png`

**Spécifications** :
- Dimensions : 1200x630px (format OG standard)
- Format : PNG ou JPG
- Poids cible : < 1MB

**Contenu suggéré** :
- Background : Dégradé spatial (bleu foncé vers violet)
- Texte : "Constellation Tech - Transformez votre CV en Constellation"
- Logo/Icône : Étoile ou constellation
- Sous-texte : "Powered by AI"

**Outils recommandés** :
- [Canva](https://www.canva.com/) - Template "Facebook Post" 1200x630
- [Figma](https://www.figma.com/) - Design personnalisé
- [OG Image Generator](https://og-image.vercel.app/)

**Template Canva à utiliser** :
1. Créer un design 1200x630px
2. Background : Gradient #0A0A14 → #1A1A2E → #16213E
3. Titre : "Constellation Tech" (Space Mono Bold, 72pt, blanc)
4. Sous-titre : "Votre CV Tech devient une Constellation Spatiale" (Space Mono Regular, 36pt, blanc 80%)
5. Ajouter quelques étoiles/particules décoratives
6. Exporter en PNG

---

### 3. Hero Background

**Fichier** : `constellation-hero-bg.png`

**Spécifications** :
- Résolution : 2560x1440px minimum (haute définition)
- Format : PNG (avec transparence) ou JPG optimisé
- Poids cible : < 500KB après compression
- Contenu : Image de constellation spatiale, nébuleuse, ou ciel étoilé

**Sources d'images gratuites** :

1. **NASA Image Library** (domaine public) :
   - https://images.nasa.gov/
   - Rechercher : "constellation", "nebula", "stars", "space"
   - Télécharger en haute résolution

2. **Unsplash** (libre de droits) :
   - https://unsplash.com/s/photos/constellation
   - https://unsplash.com/s/photos/night-sky
   - Photographes recommandés : Jeremy Thomas, NASA, Aldebaran S

3. **Pexels** (libre de droits) :
   - https://www.pexels.com/search/constellation/

4. **Générer avec Stable Diffusion** (si accès) :
   ```
   Prompt: "Beautiful space constellation, stars connected by glowing lines,
   deep blue and purple nebula background, cosmic dust, ultra realistic,
   high detail, 8k, astronomy photography"
   ```

**Optimisation de l'image** :
```bash
# Redimensionner si trop grande
convert constellation-raw.jpg -resize 2560x1440^ -gravity center -extent 2560x1440 constellation-resized.jpg

# Optimiser avec JPG progressif
convert constellation-resized.jpg -quality 85 -interlace Plane constellation-hero-bg.jpg

# Ou avec WebP (meilleure compression)
cwebp -q 85 constellation-resized.jpg -o constellation-hero-bg.webp
```

**Fallback actuel** :
Un gradient CSS est utilisé si l'image n'est pas disponible (voir `styles.css`).

---

### 4. Placeholder Temporaire

Si vous voulez tester sans images, utilisez un gradient CSS :

**Dans `styles.css`, remplacer** :
```css
.hero {
    background-image: url('assets/constellation-hero-bg.png');
}
```

**Par** :
```css
.hero {
    background: linear-gradient(
        135deg,
        #0A0A14 0%,
        #16213E 25%,
        #1A1A2E 50%,
        #0F3460 75%,
        #0A0A14 100%
    );
}
```

---

## ✅ Checklist Assets

- [ ] favicon-16x16.png généré
- [ ] favicon-32x32.png généré
- [ ] apple-touch-icon.png généré
- [ ] og-image.png créé (1200x630)
- [ ] constellation-hero-bg.png trouvé/optimisé
- [ ] Toutes les images optimisées (poids total < 1MB)

---

## 🎨 Charte Graphique

Pour garder une cohérence visuelle :

**Couleurs principales** :
- Dark Blue : `#0A0A14`
- Primary Blue : `#6496FF`
- Light Blue : `#96A0FF`
- Accent Pink : `#FF6B9D`
- White : `#FFFFFF`

**Police** :
- Space Mono (Google Fonts)
- Poids : 400 (Regular), 700 (Bold)

**Style** :
- Spatial, futuriste, moderne
- Effets de glow/lueur subtils
- Glassmorphism (transparence + blur)
- Animations fluides

---

**Besoin d'aide ?** Consultez le README.md principal pour plus d'informations.
