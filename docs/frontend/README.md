# Front-End Documentatie — FixeR

Deze documentatie beschrijft de opzet, architectuur en werkwijze van de front-end van FixeR.

Doel:
- kennis borgen
- consistentie bevorderen
- overdraagbaarheid vergroten
- herhaling voorkomen

---

De nadruk ligt op technische overdracht voor front-end ontwikkelaars die het project overnemen of onderhouden.

De documentatie is bewust beperkt tot vier centrale bestanden:

- frontend/README.md (dit document)
- [frontend/controllers/README.md](https://github.com/forza-mor-rotterdam/FixeR/blob/documentatie-frontend/docs/frontend/controllers/README.md)
- [frontend/styling/README.md](https://github.com/forza-mor-rotterdam/FixeR/blob/documentatie-frontend/docs/frontend/styling/README.md)
- [frontend/patterns/README.md](https://github.com/forza-mor-rotterdam/FixeR/blob/documentatie-frontend/docs/frontend/patterns/README.md)

---

## Doel van deze documentatie

Doelen:

- inzicht geven in de front-end architectuur
- uitleggen hoe Stimulus wordt toegepast
- beschrijven hoe styling is georganiseerd
- herbruikbare patronen vastleggen
- bekende inconsistenties benoemen

Niet bedoeld als:

- beginnershandleiding
- algemene JavaScript-cursus
- marketingdocumentatie

---

## Relatie met de hoofd-README

Basisinformatie over installatie, dependencies en algemene development workflow staat in de root README van de repository:

https://github.com/forza-mor-rotterdam/FixeR/blob/documentatie-frontend/README.md

Deze front-end documentatie verwijst daar naar voor:

- installatie van dependencies
- lokale development setup
- Docker-commando’s
- globale build/run instructies

Duplicatie van deze informatie wordt bewust vermeden.

---

## Globale front-end architectuur

FixeR is een server-side rendered applicatie op basis van Django, met client-side verrijking via JavaScript.

Hoofdprincipes:

- Django rendert HTML via templates
- Templates bevatten data-attributen voor configuratie
- SCSS en JavaScript worden gebundeld via Webpack
- Stimulus koppelt gedrag aan DOM-elementen
- Fetch/AJAX wordt beperkt ingezet (geen SPA)


---

## Ontwikkelworkflow (beknopt)

Voor volledige setup-instructies: zie [root README](https://github.com/forza-mor-rotterdam/FixeR/blob/documentatie-frontend/README.md).

Globaal:

- dependencies installeren via npm
- front-end assets bouwen via npm scripts / make
- Django server draait apart of via Docker

Typische commando’s (indicatief):

    npm install
    npm run watch
    npm run build

TODO: indien nodig project-specifiek aanvullen

---

## Build & bundling (beknopt)

De front-end assets worden gebundeld via Webpack.

Kenmerken:

- SCSS wordt gecompileerd naar CSS
- JavaScript wordt gebundeld per entry-point
- output wordt geplaatst in static/dist
- Django templates laden deze assets

Details over entry-points staan in: [styling/README.md](https://github.com/forza-mor-rotterdam/FixeR/blob/documentatie-frontend/docs/frontend/styling/README.md)

---

## Controllers

Alle informatie over Stimulus controllers staat in: [controllers/README.md](https://github.com/forza-mor-rotterdam/FixeR/blob/documentatie-frontend/docs/frontend/controllers/README.md)

Daar vind je:

- overzicht van alle controllers
- conventies en naamgeving
- prioriteiten
- aandachtspunten
- verwijzingen naar detaildocumentatie

---

## Styling (SCSS)

Alles over styling staat in: [styling/README.md](https://github.com/forza-mor-rotterdam/FixeR/blob/documentatie-frontend/docs/frontend/styling/README.md)

Inclusief:

- mapstructuur
- entry-points
- naamgeving
- theming
- technische schuld

---

## Patterns

Herbruikbare front-end patronen staan in: [patterns/README.md](https://github.com/forza-mor-rotterdam/FixeR/blob/documentatie-frontend/docs/frontend/patterns/README.md)

Inclusief:

- HTML + Stimulus integratie
- state & events
- fetch gebruik
- dialog/overlay patronen
- anti-patterns

---

## Bekende aandachtspunten

De codebase is historisch gegroeid.

Gevolgen:

- verschillen in controller-opzet
- variatie in SCSS-structuur
- gemengde patronen
- legacy oplossingen

Deze worden expliciet gedocumenteerd in de themabestanden.

---

## Aanbevolen werkwijze voor opvolgers

1. Lees dit document volledig
2. Lees [controllers/README.md](https://github.com/forza-mor-rotterdam/FixeR/blob/documentatie-frontend/docs/frontend/controllers/README.md)
3. Lees [styling/README.md](https://github.com/forza-mor-rotterdam/FixeR/blob/documentatie-frontend/docs/frontend/styling/README.md)
4. Lees [patterns/README.md](https://github.com/forza-mor-rotterdam/FixeR/blob/documentatie-frontend/docs/frontend/patterns/README.md)
5. Bekijk de [root README](https://github.com/forza-mor-rotterdam/FixeR/blob/documentatie-frontend/README.md) voor setup
6. Bestudeer daarna pas de code

---

## Onderhoud

Verantwoordelijke:
- TODO: naam of rol

Laatste update:
- TODO: datum

Wijzigingen in architectuur, tooling of patronen dienen hier te worden vastgelegd.
