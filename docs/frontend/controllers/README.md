# Stimulus Controllers — FixeR

Dit document beschrijft hoe Stimulus controllers binnen FixeR zijn opgezet, gebruikt en onderhouden.

Voor Stimulus zelf: https://stimulus.hotwired.dev

---

## Overzicht

Controllers bevinden zich in:

    app/frontend/assets/controllers/

Overzicht genereren met:

    find app -type f -name "*_controller.js"
    rg 'data-controller="' app

---

## Rol van controllers in dit project

Controllers vormen de primaire client-side laag.

Ze worden gebruikt voor:

- UI-interactie
- formulierafhandeling
- dialogs/modals
- kaarten/visualisatie
- dynamische content
- notificaties

---

## Naamgeving & structuur

### Bestanden

Conventie (meestal):

    something_controller.js
    → data-controller="something"

Afwijkingen:
- komen voor (legacy)

---

### Identifiers

- kebab-case
- domeingericht

Voorbeelden:

    task-detail
    taken-kaart
    review-form

---

## Targets, Values, Actions

### Targets

Gebruik:
- herbruikbare DOM-referenties
- vermijden van querySelector

Richtlijn:
- benoem op functie, niet op HTML-tag

---

### Values

Gebruik:
- configuratie vanuit Django
- ids, flags, strings

Let op:
- typeconversie
- JSON encoding

---

### Actions

Gebruik:
- declaratieve event-binding

Richtlijn:
- houd actions dun

---

## State & communicatie

### Interne state

Meestal via properties:

    this.isOpen
    this.currentIndex

Geen centrale state store.

---

### Communicatie

Patronen:

- custom events
- window events
- gedeelde helpers

Niet overal uniform.

---

## Afhankelijkheden

Controllers kunnen afhankelijk zijn van:

- externe libraries
- shared helpers
- backend endpoints

Geen centrale registratie.

---

## Build-integratie

Controllers worden:

- gebundeld via Webpack
- automatisch geladen

TODO: exacte registratie beschrijven

---

## Inconsistenties & technische schuld

### Grootte

Twee hoofdtypes:

1. Klein & taakgericht
2. Groot & monolithisch

Beide aanwezig.

---

### Verantwoordelijkheden

Sommige controllers combineren:

- UI
- data
- validatie
- state

Refactorpotentieel aanwezig.

---

## Overzicht per domein (FixeR)

### Taak-domein

- taken-overzicht_controller.js
- taken-lijst_controller.js
- taak_controller.js
- taak-detail_controller.js
- taakNavigatie_controller.js
- taaktypeformulier_controller.js
- incidentHandleForm_controller.js

---

### Kaart

- taken-kaart_controller.js
- kaartModus_controller.js

---

### Filtering / zoeken / sorteren

- zoekFilter_controller.js
- sorteerFilter_controller.js
- row_search_controller.js

---

### Form helpers

- form_controller.js
- selectAll_controller.js
- datetime_controller.js
- characterCount_controller.js
- dagen_uren_controller.js

---

### UI componenten

- modal_controller.js
- infosheet_controller.js
- overflow_controller.js
- lazyloader_controller.js
- hero-image_controller.js
- pageHeader_controller.js
- onboarding_controller.js
- sessionTimer_controller.js

---

### Berichten & notificaties

- berichten_beheer_controller.js
- messages_controller.js
- message_controller.js

#### Notificaties

- notificaties/manager_controller.js
- notificaties/toast_item_controller.js
- notificaties/snack_item_controller.js
- notificaties/snack_overzicht_item_controller.js

---

### Auth / app core

- login_controller.js
- main_controller.js

---

### Bijlagen

- bijlagen_controller.js

---

### Utilities / observability

- utils_controller.js
- logger_controller.js

---

# (((

## Prioriteit voor detaildocumentatie

### Hoog

- taak-detail_controller.js
- taken-overzicht_controller.js
- taken-kaart_controller.js
- notficaties/manager_controller.js
- main_controller.js
- bijlagen_controller.js

---

### Middel

- zoekFilter_controller.js
- sorteervilter_controller.js
- modal_controller.js
- infosheet_controller.js
- sessionTimer_controller.js

---

### Laag

- selectAll_controller.js
- datetime_controller.js
- characterCount_controller.js
- lazyloader_controller.js
- overflow_controller.js
- hero-image_controller.js
- logger_controller.js

# )))

---

## Toevoegen van nieuwe controllers

Richtlijn:

1. Houd controllers klein
2. Beperk verantwoordelijkheden
3. Documenteer hier
4. Voeg detailpagina toe indien complex

---

## Detaildocumentatie

Uitgebreide beschrijvingen staan in:

    controllers/details/

Structuur:

    details/
      taak-detail.md
      taken-overzicht.md
      notificaties-manager.md

---

## Checklist per controller

Bij documentatie minimaal vastleggen:

- Doel (1 zin)
- Gebruikte templates
- Targets/Values/Actions
- Afhankelijkheden
- Externe calls
- Bekende valkuilen
