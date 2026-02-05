# Stimulus Controllers — FixeR

Dit document beschrijft hoe Stimulus controllers binnen FixeR zijn opgezet, gebruikt en onderhouden.

Voor Stimulus zelf: https://stimulus.hotwired.dev

---

## Wat zijn controllers?

Binnen FixeR worden “controllers” gebruikt in de betekenis van **Stimulus controllers**.

Een controller is een JavaScript-klasse die verantwoordelijk is voor het gedrag van een specifiek deel van de gebruikersinterface.

Een controller:

- wordt gekoppeld aan een HTML-element via `data-controller`
- reageert op events via `data-action`
- heeft toegang tot specifieke DOM-elementen via `data-*-target`
- kan configuratie ontvangen via `data-*-value`

Voorbeeld (vereenvoudigd):

    <div
      data-controller="example"
      data-action="click->example#open"
      data-example-id-value="123"
    >

Een bijbehorende controller:

    export default class extends Controller {
      static targets = ['panel']

      open() {
        this.panelTarget.classList.add('is-open')
      }
    }

---

## Overzicht

Controllers bevinden zich in:

    app/frontend/assets/controllers/

Overzicht genereren met:

    find app -type f -name "*_controller.js"
    rg 'data-controller="' app

---

## Rol van controllers in dit project

In FixeR vormen controllers de primaire client-side laag.

Ze worden gebruikt voor:

- afhandelen van gebruikersinteractie
- beheren van UI-state
- openen/sluiten van modals en panels
- formulierlogica
- synchronisatie met backend endpoints
- tonen van notificaties

Controllers zorgen ervoor dat:

- HTML verantwoordelijk blijft voor structuur
- CSS verantwoordelijk blijft voor presentatie
- JavaScript verantwoordelijk blijft voor gedrag

---

## Wanneer gebruik je een nieuwe controller?

Een nieuwe controller is gerechtvaardigd wanneer:

- een UI-onderdeel eigen gedrag heeft
- er meerdere events moeten worden afgehandeld
- state nodig is
- DOM-manipulatie vereist is

Gebruik geen controller voor:

- simpele styling (CSS volstaat)
- statische content
- eenmalige kleine scripts (tenzij herbruikbaar)

---

## Levenscyclus

Stimulus controllers hebben een vaste levenscyclus:

- connect() — wordt aangeroepen bij initialisatie
- disconnect() — wordt aangeroepen bij verwijderen uit DOM

In FixeR wordt deze lifecycle soms gebruikt voor:

- registreren van event listeners
- initialiseren van state
- cleanup bij navigatie

---

## Registratie en laden van controllers

Stimulus controllers worden in FixeR centraal geregistreerd tijdens het opstarten van de front-end.

Bij het laden van de applicatie:

1. Wordt de hoofd JavaScript bundle geladen (bijv. `app.js`)
2. Wordt daarin Stimulus geïnitialiseerd
3. Worden alle controller-bestanden geïmporteerd
4. Worden controllers gekoppeld aan hun `data-controller` identifiers
5. Initialiseert Stimulus automatisch controllers in de DOM

Hierdoor hoeven controllers niet per pagina handmatig geïmporteerd te worden.

---

## Centrale bootstrap

De registratie gebeurt typisch in een centraal bestand:

    app/frontend/assets/app.js


In dit bestand wordt:

- de Stimulus Application gestart
- alle controllers geregistreerd
- eventuele globale configuratie uitgevoerd

Vereenvoudigd voorbeeld:

    import { Application } from '@hotwired/stimulus'

    import TaakDetailController from './controllers/taak-detail_controller'
    import ModalController from './controllers/modal_controller'

    const application = Application.start()

    application.register('taak-detail', TaakDetailController)
    application.register('modal', ModalController)

In FixeR gebeurt dit automatisch via een import-mechanisme:

    const application = StimulusApplication.start()
    const context = require.context('./controllers', true, /\.js$/)
    application.load(definitionsFromContext(context))

Dit zorgt ervoor dat:

- nieuwe controllers automatisch worden meegenomen in de bundle
- alleen het bestand plaatsen voldoende is

---

## Koppeling met HTML

Zodra een controller is geregistreerd, wordt deze automatisch actief op alle elementen met:

    data-controller="naam"

Voorbeeld:

    <div data-controller="taak-detail">

Stimulus zoekt naar een geregistreerde controller met dezelfde naam.

Bij match:

- wordt een instantie gemaakt
- wordt connect() aangeroepen
- worden targets en values gekoppeld

---

## Debugging van registratieproblemen

Als een controller niet werkt, controleer:

1. Bestaat het bestand?
2. Is het correct geïmporteerd in de bootstrap?
3. Klopt de naam in `data-controller`?
4. Komt de naam overeen met de registratie?
5. Zijn er bundling errors?

Handig in DevTools:

    console.log(application.controllers)

Of check in console of Stimulus gestart is.

---

## Veelvoorkomende valkuilen

- Bestandsnaam en identifier komen niet overeen
- Controller is niet toegevoegd aan de bootstrap
- Typfout in data-controller
- Oude bundle in cache
- Build niet opnieuw gedraaid

Bij twijfel: build opnieuw uitvoeren en cache legen.

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

<!-- ## Prioriteit voor detaildocumentatie

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
- logger_controller.js -->


---

## Toevoegen van nieuwe controllers

Richtlijn:

1. Houd controllers klein
2. Beperk verantwoordelijkheden
3. Documenteer hier
4. Voeg detailpagina toe indien complex

---

## Todo Detaildocumentatie

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
