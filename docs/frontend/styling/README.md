# Styling (SCSS) — FixeR

Dit document beschrijft de opzet, conventies en aandachtspunten van de SCSS-styling binnen FixeR.

---

## SCSS — Locatie en entry-points

### Locatie van de SCSS-source

Alle SCSS-bestanden liggen binnen:

    app/frontend/assets/styles/

Dit is de hoofdmap voor styling in FixeR.

Binnen deze map vind je:

- **basisbestanden**
  Variabelen, mixins, settings
- **layout-structuur**
  Grid, spacing, containerregels
- **componentstyles**
  SCSS voor specifieke UI-componenten
- **utilities**
  kleine helpers: spacing, text alignment, visibility

TODO Toon de feitelijke mapinhoud hier zodra die geïnspecteerd is

---

### Entry-points

De SCSS-entrypoints zijn de bestanden die door de bundler (“Webpack/NPM”) worden opgenomen als startpunt voor CSS-bundles.

In deze projectopzet werkt SCSS via één hoofd-entryfile dat worden geïmporteerd in de frontend build.

    // hoofd SCSS entry
    app/frontend/assets/styles/app.scss

In een standaard setup met `sass-loader` volgt de webpack-bundler vanaf deze entry alle imports (`@use`, `@import`) die in **app.scss** staan en maakt daar één CSS-bestand van.
Deze CSS-bundle wordt opgenomen door de Django templates via `<link>`

FixeR gebruikt bestandsnaam-hashing voor cache busting van **JS** en **CSS** output. Dit betekent dat browsers/CDN’s assets lang kunnen cachen, en dat bij elke nieuwe build de URL verandert (door de hash in de bestandsnaam), waardoor clients automatisch de nieuwe versie ophalen.

---

### Hoe Django de juiste bestandsnamen vindt

FixeR genereert een Webpack stats-bestand via webpack-bundle-tracker:

    new BundleTracker({ filename: './public/build/webpack-stats.json' })

Dit bestand bevat (typisch) een mapping van logical bundle names (bijv. `app`) naar de daadwerkelijke output filenames (bijv. `app-a1b2c3d4e5.js` en `app-a1b2c3d4e5.css`).

Django kan dit stats-bestand gebruiken om in templates altijd de juiste hashed bestandsnamen te includen.

TODO:
- beschrijf welke Django template tag/helper gebruikt wordt om `webpack-stats.json` te lezen
- noteer waar die code staat (bijv. een template tag module)

---

### Output locatie en publicPath

Webpack schrijft bestanden naar:

    output.path = './public/build/'

En publicPath is:

    output.publicPath = '/static/'

Dit betekent:
- bestanden staan fysiek in `app/frontend/public/build/` (relatief aan webpack context)
- URLs die Webpack in runtime/manifest gebruikt beginnen met `/static/`

In development wordt output.path expliciet opnieuw gezet naar dezelfde map, en wordt filename hashing uitgezet voor JS:

    config.output.path = './public/build/'
    config.output.filename = '[name].js'

---

### Overige assets (images/icons/script/manifest)

Assets worden gekopieerd met CopyWebpackPlugin:

- images → `images/[name][ext]`
- icons  → `icons/[name][ext]`
- script → `script/[name][ext]`
- manifest.json → `[name][ext]`

Deze bestanden krijgen géén hash in de naam.

Scripts van externe libraries worden wordt apart opgenomen door de Django templates via `<link>`

---
### Samenvatting

- SCSS staat in: `app/frontend/assets/styles/`
- Entry-points één enkel SCSS-bestand binnen die map
- De bundler (Webpack) volgt vanaf die entry alle imports naar partials
- De gegenereerde CSS-bundle wordt opgenomen via Django templates

---

## Architectuur van styling

Globale opzet (indicatief):

- base / variables
- layout
- components
- utilities
- overrides

Niet overal strikt toegepast (historisch gegroeid).

---

## Import-structuur

Richtlijn (voorkeur):

    variables
      → base
        → layout
          → components
            → utilities
              → overrides

---

## Naamgeving

### Klassen

Voorkeur:
- semantisch
- componentgericht
- geen layoutdetails

Voorbeelden:

    .task-card
    .review-form
    .map-panel

---

### Bestanden

Voorkeur:

    _component-name.scss
    _layout-name.scss

---

## Component styling

Richtlijnen:

- één primair SCSS-bestand per component
- vermijd diepe nesting (>3 niveaus)
- geen afhankelijkheid van exacte DOM-structuur

Realiteit:
- legacy uitzonderingen bestaan

---

## Layout & responsive

### Breakpoints

TODO: locatie en definities

---

### Strategie

TODO:
- mobile-first / desktop-first
- container queries?
- media query helpers?

---

## Theming & overrides

TODO:
- klant-specifieke styling?
- omgeving-afhankelijk?
- hoe georganiseerd?

Let op risico op cascade-conflicten.

---

## Inconsistenties & technische schuld

### Legacy styles

Kenmerken:

- globale selectors
- hoge specificity
- !important
- afhankelijkheid van volgorde

---

### Cascade-problemen

Voorbeelden:

- overrides zonder context
- moeilijk te traceren styles
- regressies bij refactor

---

## Toevoegen van nieuwe styling

Richtlijn:

1. Bepaal of het component of layout is
2. Maak/gebruik bestaand bestand
3. Volg naamgeving
4. Test op meerdere schermgroottes
5. Documenteer afwijkingen

---

<!-- ## Detaildocumentatie

Uitgebreide documentatie per component of module staat in:

    styling/details/

Structuur:

    details/
      dialogs.md
      forms.md
      map.md
      tables.md

Gebruik dit alleen voor complexe styling.

--- -->

## Checklist bij aanpassingen

Bij grotere wijzigingen:

- impact op andere pagina’s getest
- cascade gecontroleerd
- responsive gedrag nagekeken
- documentatie bijgewerkt
