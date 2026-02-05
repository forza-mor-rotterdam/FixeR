# Styling (SCSS) — FixeR

Dit document beschrijft de opzet, conventies en aandachtspunten van de SCSS-styling binnen FixeR.

Doel:
- overdracht vereenvoudigen
- consistentie bevorderen
- technische schuld zichtbaar maken
- uitbreidingen beheersbaar houden

---

## SCSS — Locatie en entry-points

### Locatie van de SCSS-source

Alle SCSS-bestanden liggen binnen:

    app/frontend/assets/styles/

Dit is de hoofdmap voor styling in FixeR.

Binnen deze map vind je doorgaans:

- **basisbestanden**
  Variabelen, mixins, settings
- **layout-structuur**
  Grid, spacing, containerregels
- **componentstyles**
  SCSS voor specifieke UI-componenten
- **utilities**
  kleine helpers: spacing, text alignment, visibility

(Toon de feitelijke mapinhoud hier zodra die geïnspecteerd is)

---

### Entry-points

De SCSS-entrypoints zijn de bestanden die door de bundler (“Webpack/NPM”) worden opgenomen als startpunt voor CSS-bundles.

In deze projectopzet werkt SCSS via één hoofd-entryfile dat worden geïmporteerd in de frontend build.

Een typisch patroon dat we in projecten met Webpack zien, is:

    // hoofd SCSS entry
    app/frontend/assets/styles/app.scss

De bundler volgt vanaf deze entry’s alle imports (`@use`, `@import`) en maakt daar één of meerdere CSS-bestanden van. :contentReference[oaicite:1]{index=1}

Zonder exacte webpack.config.js-weergave gaan we ervan uit dat:

- **app.scss** de primaire entry is
- Andere partials (`_*.scss`) worden enkel via imports gebruikt, niet direct als entry

> Belangrijk: Webpack vereenvoudigt SCSS-bundling door één of meerdere main entry files op te geven in `entry` (in webpack.config.js). Die bestanden vormen de basis van wat er uiteindelijk in de gegenereerde CSS-bundle terechtkomt. :contentReference[oaicite:2]{index=2}

---

### Hoe SCSS wordt gebundeld

In een standaard setup met `sass-loader` (Webpack):

- SCSS verzamelt alle dependencies via `@use`/`@import`
- Op basis van de entry’s maakt Webpack één of meerdere CSS-bundles
- Deze CSS-bundles worden opgenomen door de Django templates via `<link>` of via template tags

TODO: exacte bundlename(s) en output-location toevoegen zodra de webpack.config.js bekend is

---

### Webpack entry-points (SCSS)

De SCSS wordt gebundeld via Webpack met als entry-point

    ./app/frontend/assets/styles/app.scss'

Vanaf dit bestand volgt Webpack alle `@use` / `@import` statements en genereert één CSS-bundle.

De gegenereerde CSS-bestanden worden geplaatst in:

    app/frontend/static/dist/

En via Django templates ingeladen.


---

### Samenvatting

- SCSS staat in: `app/frontend/assets/styles/` :contentReference[oaicite:4]{index=4}
- Entry-points zijn waarschijnlijk één of enkele SCSS-bestanden binnen die map
- De bundler (Webpack) volgt vanaf die entry’s alle imports naar partials
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

TODO: feitelijke import-volgorde documenteren

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

TODO: feitelijke conventies vastleggen

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

## Integratie met build

SCSS wordt:

- gecompileerd via Webpack
- gebundeld in CSS-assets
- geleverd via Django staticfiles

TODO: exacte pipeline beschrijven

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

## Detaildocumentatie

Uitgebreide documentatie per component of module staat in:

    styling/details/

Structuur:

    details/
      dialogs.md
      forms.md
      map.md
      tables.md

Gebruik dit alleen voor complexe styling.

---

## Checklist bij aanpassingen

Bij grotere wijzigingen:

- impact op andere pagina’s getest
- cascade gecontroleerd
- responsive gedrag nagekeken
- documentatie bijgewerkt
