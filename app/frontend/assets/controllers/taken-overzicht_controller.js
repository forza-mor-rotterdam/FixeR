import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static outlets = ['taken-kaart']

  static targets = [
    'sorteerOptiesFieldContainer',
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
  ]
  initialize() {
    this.kaartModus = null
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
    this.to = setTimeout(() => {
      this.clearSelectedTaakUuidField()
      this.element.requestSubmit()
    }, 200)
  }
  positionChangeEvent(position) {
    this.gpsFieldTarget.value = `${position.coords.latitude},${position.coords.longitude}`
    this.clearSelectedTaakUuidField()
    this.element.requestSubmit()
  }
  positionWatchError() {
    this.gpsFieldTarget.value = ''
    this.element.requestSubmit()
  }
  onSearchChangeHandler(e) {
    clearTimeout(this.to)
    this.to = setTimeout(() => {
      this.clearSelectedTaakUuidField()
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
    const li = e.target.closest('li')
    Array.from(e.target.closest('ul').querySelectorAll('li')).map((elem) => {
      elem.classList[li == elem ? 'add' : 'remove']('active')
    })
    this.kaartModus = e.target.value
    if (this.hasTakenKaartOutlet) {
      this.takenKaartOutlet.kaartModusChangeHandler(this.kaartModus)
    }
    this.element.requestSubmit()
  }
  takenKaartOutletConnected() {
    setTimeout(() => {
      if (this.hasTakenKaartOutlet) {
        this.takenKaartOutlet.kaartModusChangeHandler(this.kaartModus)
      }
    }, 1)
  }
  kaartModusOptionTargetConnected(kaartModusOption) {
    this.kaartModus = kaartModusOption.checked ? kaartModusOption.value : this.kaartModus
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
}
