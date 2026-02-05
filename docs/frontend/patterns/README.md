# Patterns — FixeR

Dit document beschrijft terugkerende technische patronen in de front-end van FixeR.


## HTML + Stimulus integratie

Standaard patroon:

- Django rendert HTML
- data-attributen configureren gedrag
- Stimulus koppelt logica

Voorbeeld:

    <div
      data-controller="example"
      data-action="click->example#open"
    >

---

## Data vanuit Django

Gebruikelijke patronen:

1. data-*-value (primitives)
2. JSON blobs (arrays/objects)
3. hidden inputs (incidenteel)

Let op:

- escaping
- quotes
- payload-grootte

TODO: voorbeelden uit FixeR toevoegen

---

## State management

Geen centrale state store.

Gebruik:

- controller properties
- Stimulus values
- DOM-state

Voorbeeld:

    this.isOpen = false
    this.currentIndex = 0

---

## Custom events

Gebruik:

    window.dispatchEvent(
      new CustomEvent("dialog:open")
    )

Richtlijnen:

- naamgeving documenteren
- listeners opruimen
- coupling vermijden

TODO: centrale eventlijst bijhouden

---

## API / fetch patterns

Basispatroon:

    fetch(url, options)

Meestal met:

- CSRF token
- JSON handling
- error states
- loading indicators

TODO: standaard wrapper beschrijven (indien aanwezig)

---

## Dialogs & overlays

Veelgebruikte patronen:

- <dialog>
- custom modals
- bottom sheets
- backdrops

Aandachtspunten:

- focus trapping
- scroll locking
- iOS/Safari gedrag

---

## Performance patterns

Gebruikte optimalisaties:

- debouncing scroll
- throttling resize
- lazy loading
- image preloading

Niet overal consequent toegepast.

---

## Error handling

Richtlijnen:

- fouten zichtbaar maken voor gebruiker
- console logging in dev
- beperkte logging in productie

TODO: project-specifieke afspraken

---

## Anti-patterns

Bekend:

- te grote controllers
- verborgen afhankelijkheden
- logica in templates
- inline scripts
- duplicatie van state

Deze komen voor; wees bewust.

---

## Toevoegen van nieuwe patterns

Nieuwe patronen:

1. Documenteer hier
2. Motiveer de keuze
3. Voeg voorbeeld toe
4. Stem af met team

---

## Detaildocumentatie (nodig?)

Uitgebreide beschrijvingen staan in:

    patterns/details/

Structuur:

    details/
      dialogs.md
      api-wrapper.md
      state-sync.md
