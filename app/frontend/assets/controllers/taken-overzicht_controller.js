import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

export default class extends Controller {
  static outlets = ['taken-kaart', 'taken-lijst']

  static targets = [
    'sorteerOptiesFieldContainer',
    'sorteerField',
    'zoekFieldset',
    'zoekFieldContainer',
    'zoekFieldDefaultContainer',
    'toggleMapView',
    'toggleZoeken',
    'filterInput',
    'cancelZoek',
    'zoekField',
    'filterButton',
    'pageField',
    'gpsField',
    'selectedChoicesCount',
    'selectedChoicesTotalCount',
    'takenKaart',
    'kaartModusOption',
    'taakItem',
    'taakPopup',
    'containerHeader',
    'selectedTaakUuidField',
    'taakAfstand',
    'filtersActiveField',
  ]

  initialize() {
    this.kaartModus = null
    this.currentPosition = null
    window.addEventListener('resize', (e) => this.onResizeHandler(e))
    this.onResizeHandler()
    this.updateSelectedChoicesCount()
  }
  onResizeHandler() {
    if (
      window.innerWidth < 1024 &&
      this.zoekFieldsetTarget.parentNode != this.zoekFieldContainerTarget
    ) {
      this.zoekFieldContainerTarget.insertAdjacentElement('beforeEnd', this.zoekFieldsetTarget)
    }
    if (
      window.innerWidth >= 1024 &&
      this.zoekFieldsetTarget.parentNode != this.zoekFieldDefaultContainerTarget
    ) {
      this.zoekFieldDefaultContainerTarget.insertAdjacentElement(
        'beforeEnd',
        this.zoekFieldsetTarget
      )
    }
  }
  connect() {
    const urlObj = new URL(window.location.href)
    urlObj.search = ''
    const url = urlObj.toString()
    window.history.replaceState({}, '', url)
    if (
      this.hasTakenLijstOutlet &&
      this.hasSelectedTaakUuidFieldTarget &&
      this.selectedTaakUuidFieldTarget.value
    ) {
      setTimeout(() => {
        this.takenLijstOutlet.selectTaakMarker({
          params: { taakUuid: this.selectedTaakUuidFieldTarget.value, preventScroll: false },
        })
      }, 800)
    }

    if (this.filtersActiveFieldTarget.checked) {
      this.zoekFieldContainerTarget.classList.remove('hidden-vertical')
      this.zoekFieldContainerTarget.classList.add('show-vertical')
    }
  }
  keydownHandler(e) {
    // Check if Enter was pressed without Shift, Ctrl, Alt, Caps
    if (
      e.key === 'Enter' &&
      !e.shiftKey &&
      !e.ctrlKey &&
      !e.altKey &&
      !e.capsLockKey &&
      document.activeElement === this.zoekFieldTarget
    ) {
      e.preventDefault()
      this.submit()
    }
  }
  clearSelectedTaakUuidField() {
    this.selectedTaakUuidFieldTarget.value = ''
  }
  updateSelectedChoicesCount() {
    this.selectedChoicesCountTargets.map((elem) => {
      let container = elem.closest('details.filter')
      if (!container || container.classList.contains('filter--active')) {
        container = elem.closest('form')
      }
      elem.textContent = `${
        Array.from(container.querySelectorAll('li.filter-option-container input:checked')).length
      }`
    })
  }

  removeFilter(e) {
    const input = document.querySelector(`[name="${e.params.name}"][value="${e.params.value}"]`)
    input.checked = false
    this.updateSelectedChoicesCount()
  }
  onChangeFilter() {
    this.updateSelectedChoicesCount()
    this.clearSelectedTaakUuidField()
    this.submit()
  }
  selectAll(e) {
    const checkList = Array.from(e.target.closest('details').querySelectorAll('.form-check-input'))
    const doCheck = e.params.filterType === 'all'
    checkList.forEach((element) => {
      element.checked = doCheck
    })
    this.updateSelectedChoicesCount()
  }
  removeAllFilters() {
    this.filterInputTargets.checked = false
    this.filterInputTargets.forEach((input) => {
      input.checked = false
    })
    this.updateSelectedChoicesCount()
  }
  onCancelSearch() {
    this.zoekFieldTarget.value = ''
    this.cancelZoekTarget.classList.add('hide')
    this.toggleZoekenTarget.disabled = false
    this.zoekFieldTarget.focus()
    this.clearSelectedTaakUuidField()
    this.submit()
  }
  positionChangeEvent(position) {
    this.currentPosition = position
    this.gpsFieldTarget.value = `${position.coords.latitude},${position.coords.longitude}`
    if (this.sorteerFieldTarget.value === 'Afstand') {
      this.submit()
    }
    this.updateTaakAfstandTargets()
  }
  positionWatchError() {
    this.gpsFieldTarget.value = ''
    this.currentPosition = null
    this.element.requestSubmit()
  }

  onZoekButtonClick() {
    this.submit()
  }
  onSearchChangeHandler(e) {
    const zoekHasValue = e.target.value.length > 0
    this.toggleZoekenTarget.disabled = zoekHasValue
    this.zoekFieldContainerTarget.classList.remove('hidden-vertical')
    this.zoekFieldContainerTarget.classList.add('show-vertical')
    // this.submit()
    this.cancelZoekTarget.classList[zoekHasValue ? 'remove' : 'add']('hide')
    this.clearSelectedTaakUuidField()
  }
  onSortingChangeHandler() {
    this.clearSelectedTaakUuidField()
    this.submit()
  }
  onFiltersActiveChangeHandler() {
    this.submit()
    this.updateFilterButtonEnabled()
  }
  onPageClickEvent(e) {
    this.pageFieldTarget.value = e.params.page
    this.clearSelectedTaakUuidField()
    this.submit()
  }
  kaartModusOptionClickHandler(e) {
    this.setKaartModus(e.target.value)
  }
  setKaartModus(kaartModus) {
    this.kaartModusOptionTargets
      .find((elem) => elem.value === 'volgen')
      .closest('li')
      .classList[kaartModus === 'volgen' ? 'add' : 'remove']('active')
    if (this.hasTakenKaartOutlet) {
      this.takenKaartOutlet.kaartModusChangeHandler(kaartModus)
    }
    this.submit()
  }
  taakAfstandTargetConnected(taakAfstand) {
    if (this.currentPosition) {
      const markerLocation = new L.LatLng(
        taakAfstand.dataset.latitude,
        taakAfstand.dataset.longitude
      )
      taakAfstand.textContent = this.formatDistance(
        Math.round(
          markerLocation.distanceTo([
            this.currentPosition.coords.latitude,
            this.currentPosition.coords.longitude,
          ])
        )
      )
    }
  }
  updateTaakAfstandTargets() {
    this.taakAfstandTargets.forEach((elem) => {
      this.taakAfstandTargetConnected(elem)
    })
  }
  onToggleSortingContainer() {
    this.sorteerOptiesFieldContainerTarget.classList.toggle('hidden-vertical')
    this.sorteerOptiesFieldContainerTarget.classList.toggle('show-vertical')
  }
  onToggleSearchContainer() {
    if (!this.zoekFieldTarget.value) {
      this.zoekFieldContainerTarget.classList.toggle('hidden-vertical')
      this.zoekFieldContainerTarget.classList.toggle('show-vertical')
      if (
        this.zoekFieldContainerTarget.classList.contains('hidden-vertical') &&
        this.filtersActiveFieldTarget.checked
      ) {
        this.filtersActiveFieldTarget.checked = false
        this.submit()
        this.updateFilterButtonEnabled()
      }
    }
  }
  filterButtonTargetConnected() {
    this.updateFilterButtonEnabled()
  }
  updateFilterButtonEnabled() {
    if (this.hasFilterButtonTarget) {
      this.filterButtonTarget.disabled = this.filtersActiveFieldTarget.checked
    }
  }
  toggleMapViewHandler() {
    this.element.classList.toggle('showMap')
  }
  showFilters() {
    this.element.classList.add('show-filters')
  }

  hideFilters() {
    this.element.classList.remove('show-filters')
  }
  takenLijstOutletConnected() {
    this.updateTaakAfstandTargets()
  }

  submit() {
    clearTimeout(this.to)
    this.to = setTimeout(() => {
      this.clearSelectedTaakUuidField()
      this.element.requestSubmit()
    }, 200)
  }

  formatDistance(meters) {
    if (meters < 50) {
      return `${Math.round(meters)} m`
    }
    if (meters < 96) {
      return `${Math.round(meters / 5) * 5} m`
    }
    const km = meters / 1000
    if (km < 100) {
      return `${(Math.round(km * 10) / 10).toLocaleString('nl-NL', {
        minimumFractionDigits: 1,
      })} km`
    }
    return `${Math.round(km).toLocaleString('nl-NL')} km`
  }
}
