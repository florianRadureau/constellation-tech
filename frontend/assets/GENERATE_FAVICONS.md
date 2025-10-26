# Génération des Favicons

Un fichier SVG `favicon.svg` est fourni comme base.

## Option 1 : Conversion Automatique avec ImageMagick

Si vous avez ImageMagick installé :

```bash
cd assets/

# Convertir le SVG en PNG haute résolution
convert favicon.svg -resize 180x180 apple-touch-icon.png

# Générer les autres tailles
convert apple-touch-icon.png -resize 32x32 favicon-32x32.png
convert apple-touch-icon.png -resize 16x16 favicon-16x16.png

echo "✓ Favicons générés avec succès !"
```

## Option 2 : Utiliser favicon.io (Recommandé - plus simple)

1. Allez sur **https://favicon.io/favicon-generator/**
2. Choisissez "Text" ou "Emoji"
3. Configuration suggérée :
   - **Text** : ⭐ (emoji étoile) ou "CT"
   - **Shape** : Rounded
   - **Background Color** : #0A0A14
   - **Font Color** : #6496FF
   - **Font Family** : Space Mono
   - **Font Size** : 80
4. Cliquez "Download"
5. Extrayez le ZIP et copiez les fichiers PNG dans `assets/`

## Option 3 : Conversion en ligne

1. Allez sur **https://www.aconvert.com/image/svg-to-png/**
2. Uploadez `favicon.svg`
3. Définissez la taille : 180x180
4. Téléchargez `apple-touch-icon.png`
5. Répétez pour 32x32 → `favicon-32x32.png`
6. Répétez pour 16x16 → `favicon-16x16.png`

## Option 4 : Utiliser Inkscape

```bash
# Installer Inkscape
sudo apt install inkscape  # Linux
brew install inkscape      # macOS

# Convertir
inkscape favicon.svg -w 180 -h 180 -o apple-touch-icon.png
inkscape favicon.svg -w 32 -h 32 -o favicon-32x32.png
inkscape favicon.svg -w 16 -h 16 -o favicon-16x16.png
```

## Vérification

Après génération, vous devriez avoir :
```
assets/
├── favicon-16x16.png
├── favicon-32x32.png
└── apple-touch-icon.png
```

Testez dans le navigateur en ouvrant `index.html` et en vérifiant l'onglet.

---

**Note** : Le fichier SVG est fourni comme fallback. Les navigateurs modernes supportent les favicons SVG, mais les PNG sont plus compatibles avec les anciens navigateurs et les appareils mobiles.
