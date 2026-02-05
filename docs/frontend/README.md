# Front-End Documentatie — FixeR

Deze documentatie beschrijft de opzet en werking van de front-end van FixeR.

Focus: technische overdracht aan een ervaren front-end ontwikkelaar.

---

## Doelgroep

Deze documentatie is bedoeld voor ontwikkelaars met kennis van:

- JavaScript
- HTML/CSS
- Template-systemen
- MVC-achtige architecturen

---

## Overzicht

De front-end bestaat uit:

- Django templates (server-side rendering)
- SCSS voor styling
- JavaScript voor interactiviteit
- Stimulus voor componentgedrag
- Webpack/NPM voor bundling

De applicatie maakt deel uit van een bredere MOR-applicatie-omgeving.

---

## Technologie-stack

### Kern

- JavaScript (ES6+)
- SCSS
- Django templates
- Hotwired Stimulus
- Webpack / NPM

### Externe libraries

- TODO: belangrijkste libraries

### Referenties

- Stimulus: https://stimulus.hotwired.dev
- TODO: overige documentatie

---

## Ontwikkelworkflow

### Installatie

Hier komt:
- hoe je frontend dependencies installeert
- waar dat gebeurt
- eventuele vereisten

Voorbeeld:
- npm install
- docker setup

TODO: projectspecifiek invullen

---

### Development

Hier komt:
- hoe je lokaal ontwikkelt
- watchers
- hot reload
- dev-servers

Voorbeeld:
- npm run watch
- make run_frontend

TODO: projectspecifiek invullen

---

### Build

Hier komt:
- hoe productie-assets worden gebouwd
- waar output terechtkomt
- wie build triggert (CI, handmatig)

Voorbeeld:
- npm run build
- webpack config

TODO: projectspecifiek invullen

---

### Debugging

Hier komt:
- hoe je frontend problemen opspoort
- logging
- browser devtools
- bekende valkuilen

Voorbeeld:
- console logging
- source maps
- network tab

TODO: projectspecifiek invullen

---

## Architectuur (globaal)

Hier beschrijf je:

- hoe frontend en backend samenwerken
- hoe data van Django → JS gaat
- hoe templates + Stimulus koppelen
- hoe pagina’s worden opgebouwd

Niet hier:
- concrete codevoorbeelden
- specifieke controllers

Voorbeeldstructuur:

- Django rendert HTML
- data via data-attributen
- Stimulus koppelt gedrag
- fetch voor updates

TODO: projectspecifiek invullen

---

## Stimulus-gebruik

Hier beschrijf je:

- hoe controllers zijn opgezet
- naming
- targets/values/actions
- communicatiepatronen

Details per controller staan in controllers/.

---

## Styling

Hier beschrijf je:

- SCSS-structuur
- naamgeving
- component-opzet
- theming

Details staan in styling/.

---

## Structuur van de documentatie

- controllers/
  Beschrijving per Stimulus-controller

- styling/
  SCSS-structuur en conventies

- patterns/
  Terugkerende technische patronen

---

## Bekende aandachtspunten

### Inconsistenties

Hier beschrijf je:
- verschillen tussen controllers
- legacy code
- historische uitzonderingen

---

### Technische schuld

Hier beschrijf je:
- refactor-kansen
- kwetsbare delen
- problematische patronen

---

## Werkwijze voor opvolgers

Aanbevolen volgorde:

1. Lees deze README
2. Bestudeer controllers/
3. Bekijk styling/
4. Pas kleine dingen aan
5. Documenteer wijzigingen

---

## Onderhoud

Verantwoordelijke:
- TODO

Laatste update:
- TODO
