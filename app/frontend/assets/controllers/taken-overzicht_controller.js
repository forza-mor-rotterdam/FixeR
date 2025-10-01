import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

export default class extends Controller {
  static outlets = ['taken-kaart', 'taken-lijst']

  static targets = [
    'sorteerOptiesFieldContainer',
    'sorteerField',
    'zoekFieldContainer',
    'zoekFieldDefaultContainer',
    'toggleMapView',
    'filterInput',
    'cancelZoek',
    'zoekField',
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
      this.zoekFieldTarget.parentNode != this.zoekFieldContainerTarget
    ) {
      this.zoekFieldContainerTarget.insertAdjacentElement('beforeEnd', this.zoekFieldTarget)
    }
    if (
      window.innerWidth >= 1024 &&
      this.zoekFieldTarget.parentNode != this.zoekFieldDefaultContainerTarget
    ) {
      this.zoekFieldDefaultContainerTarget.insertAdjacentElement('beforeEnd', this.zoekFieldTarget)
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
    this.element.requestSubmit()
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
    this.zoekFieldTarget.focus()
    this.clearSelectedTaakUuidField()
    clearTimeout(this.to)
    this.to = setTimeout(() => {
      this.element.requestSubmit()
    }, 200)
  }
  positionChangeEvent(position) {
    this.currentPosition = position
    this.gpsFieldTarget.value = `${position.coords.latitude},${position.coords.longitude}`
    if (this.sorteerFieldTarget.value === 'Afstand') {
      this.element.requestSubmit()
    }
    this.updateTaakAfstandTargets()
  }
  positionWatchError() {
    this.gpsFieldTarget.value = ''
    this.currentPosition = null
    this.element.requestSubmit()
  }
  onSearchChangeHandler(e) {
    this.clearSelectedTaakUuidField()
    clearTimeout(this.to)
    this.to = setTimeout(() => {
      this.element.requestSubmit()
    }, 200)

    this.cancelZoekTarget.classList[e.target.value.length > 0 ? 'remove' : 'add']('hide')
  }
  onSortingChangeHandler() {
    this.clearSelectedTaakUuidField()
    this.element.requestSubmit()
  }
  onPageClickEvent(e) {
    this.pageFieldTarget.value = e.params.page
    this.clearSelectedTaakUuidField()
    this.element.requestSubmit()
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
  }
  taakAfstandTargetConnected(taakAfstand) {
    if (this.currentPosition) {
      const markerLocation = new L.LatLng(
        taakAfstand.dataset.latitude,
        taakAfstand.dataset.longitude
      )
      taakAfstand.textContent = Math.round(
        markerLocation.distanceTo([
          this.currentPosition.coords.latitude,
          this.currentPosition.coords.longitude,
        ])
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
    this.zoekFieldContainerTarget.classList.toggle('hidden-vertical')
    this.zoekFieldContainerTarget.classList.toggle('show-vertical')
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
}
