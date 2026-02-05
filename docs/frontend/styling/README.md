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

### Breakpoints (responsive)

FixeR gebruikt een centrale SCSS breakpoint-definitie op basis van `$grid-breakpoints`.

Deze staat in:

    app/frontend/assets/styles/_theme.scss

Definitie:

    $grid-breakpoints: (
        xs: 0,
        sm: 576px,
        md: 768px,
        lg: 1024px,
        xl: 1280px,
        xxl: 1440px,
    );

Deze breakpoints worden in de code gebruikt via:

    map-get($grid-breakpoints, <key>)

Voorbeeld:

    @media (min-width: map-get($grid-breakpoints, md)) { ... }

---

### Strategie: mobile-first

De styling is primair **mobile-first** opgezet.

Dit betekent:

- basis-styling = voor kleine schermen
- grotere schermen = uitbreidingen via `min-width`

Standaard patroon:

    @media (min-width: map-get($grid-breakpoints, md))

Uitzonderingen met `max-width` komen voor, maar zijn niet dominant.

---

### Overzicht van breakpoints

| Key | Waarde  | Doelgroep / Gebruik |
|-----|---------|---------------------|
| xs  | 0px     | Default / kleinste schermen |
| sm  | 576px   | Grote telefoons / kleine tablets |
| md  | 768px   | Tablets / kleine laptops |
| lg  | 1024px  | Desktop / brede layouts |
| xl  | 1280px  | Grote desktops |
| xxl | 1440px  | Zeer brede schermen |

---

### Gebruik in de codebase

Op basis van analyse van de SCSS:

### sm (≥ 576px)

Gebruik:
- lichte layout-aanpassingen
- extra spacing
- kleine UI-optimalisaties

Vooral gebruikt in:
- page header
- map
- notifications
- lists

---

### md (≥ 768px)

Belangrijkste structurele breakpoint.

Gebruik:
- switch van stacked → columns
- grotere formulieren
- complexere layouts

Veel gebruikt in:
- forms
- filters
- lists
- base
- unauthorized pages

---

### lg (≥ 1024px)

Primair desktop-breakpoint.

Gebruik:
- two-panel layouts
- sidebars
- grotere overzichten
- kaartweergave

Veel gebruikt in:
- incident details
- notifications
- onboarding
- list-incidents
- beheer-pagina’s

---

### xl / xxl (≥ 1280px / ≥ 1440px)

Momenteel beperkt gebruikt.

Doel:
- optimalisatie voor zeer brede schermen
- extra witruimte / schaalbaarheid

Gebruik hiervan is (nog) niet overal consistent.

---

## Uitzonderingen

### Hardcoded widths

In enkele bestanden komt een vaste waarde voor, bijvoorbeeld:

    @media (max-width: 1023px)

Dit wijkt af van `$grid-breakpoints` (lg = 1024px).

Deze regels zijn waarschijnlijk historisch gegroeid of device-specifiek en worden beschouwd als technische schuld, tenzij expliciet gemotiveerd.

---

### max-width media queries

Sommige componenten gebruiken:

    @media (max-width: map-get($grid-breakpoints, lg))

Dit wordt meestal toegepast wanneer:

- een “mobile/tablet”-layout tot en met lg geldt
- en vanaf lg een desktopvariant actief wordt

Gebruik dit patroon bewust en documenteer het bij complexe componenten.

---

## Richtlijnen voor nieuw werk

Bij nieuwe styling:

1. Gebruik altijd `$grid-breakpoints` via `map-get`
2. Werk mobile-first (`min-width`)
3. Vermijd hardcoded pixelwaarden
4. Gebruik `max-width` alleen met duidelijke reden
5. Documenteer afwijkingen

---

## Technische schuld

Bekend:

- incidenteel gebruik van vaste widths
- beperkte toepassing van xl/xxl
- enkele component-specifieke uitzonderingen

Bij refactors: voorkeur voor centralisatie via `$grid-breakpoints`.

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
