import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

let scrollPositionForDialog = 0
let filterCount = 0
export default class extends Controller {
  static outlets = ['taken-kaart', 'taken-lijst']

  static targets = [
    'sorteerOptiesFieldContainer',
    'sorteerField',
    'zoekFieldset',
    'zoekFieldContainer',
    'zoekFieldDefaultContainer',
    'toggleMapView',
    'toggleSortView',
    'toggleZoeken',
    'filtersheet',
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
    'scrollHandle',
    'filterCount',
    'zoekButton',
    'uitklapper',
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

    if (this.filtersActiveFieldTarget.checked || this.zoekFieldTarget.value.length > 0) {
      this.zoekFieldDefaultContainerTarget.classList.remove('hidden-vertical')
      this.zoekFieldDefaultContainerTarget.classList.add('show-vertical')
      this.zoekFieldContainerTarget.classList.remove('hidden-vertical')
      this.zoekFieldContainerTarget.classList.add('show-vertical')
      this.zoekFieldTarget.focus()
      const l = this.zoekFieldTarget.value.length
      this.zoekFieldTarget.setSelectionRange(l, l)
    }
    document.addEventListener('click', this.closeAll)
  }

  disconnect() {
    document.removeEventListener('click', this.closeAll)
  }

  toggle(event) {
    event.stopPropagation()
    const current = event.currentTarget.closest('[data-taken-overzicht-target="uitklapper"]')
    this.uitklapperTargets.forEach((el) => {
      if (el !== current) el.classList.remove('show')
    })

    current.classList.toggle('show')
  }

  closeAll = (event) => {
    if (this.element.contains(event.target)) return

    this.element.classList.remove('show')
  }

  allDropdowns() {
    return document.querySelectorAll('.container__uitklapper')
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
  scrollHandleTargetConnected(element) {
    this.startX = 0
    this.startY = 0
    this.currentX = 0
    this.currentY = 0
    this.isSwiping = false
    if ('ontouchstart' in window) {
      element.addEventListener('touchstart', (e) => {
        this.handleTouchStart(e)
      })

      element.addEventListener('touchmove', (e) => {
        this.handleTouchMove(e)
      })

      element.addEventListener('touchend', () => {
        this.handleTouchEnd()
      })
    }
  }

  handleTouchStart(e) {
    this.startX = e.touches[0].clientX
    this.startY = e.touches[0].clientY
    this.currentX = this.startX // in het geval gebruiker alleen mmar tapt ipv swipet
    this.currentY = this.startY
    this.isSwiping = true
  }
  handleTouchMove(e) {
    if (!this.isSwiping) return
    this.currentX = e.touches[0].clientX
    this.currentY = e.touches[0].clientY

    const deltaX = this.currentX - this.startX
    const deltaY = this.currentY - this.startY

    if (Math.abs(deltaY) > Math.abs(deltaX)) {
      e.preventDefault()
      if (deltaY > 0) {
        this.filtersheetTarget.style.transform = `translateY(${deltaY}px)`
      }
    }
  }

  handleTouchEnd() {
    if (!this.isSwiping) return
    const swipeDistance = this.startY + this.currentY
    if (swipeDistance > 100) {
      this.filtersheetTarget.style.transform = ``
      this.hideFilters()
    } else if (swipeDistance < 10) {
      // Reset positie als swipe te kort is
      this.filtersheetTarget.style.transform = `translateY(0)`
    } else {
      // Reset positie als swipe te kort is
      this.filtersheetTarget.style.transform = `translateY(0)`
    }
  }

  updateSelectedChoicesCount() {
    this.selectedChoicesCountTargets.map((elem) => {
      let container = elem.closest('details.filter')
      if (!container || container.classList.contains('filter--active')) {
        container = elem.closest('form')
      }
      filterCount = Array.from(
        container.querySelectorAll('li.filter-option-container input:checked')
      ).length
      elem.textContent = `${filterCount}`
      if (elem.parentElement.type === 'button') {
        if (filterCount > 0) {
          elem.parentElement.querySelector('.icon').classList.add('active')
        } else {
          elem.parentElement.querySelector('.icon').classList.remove('active')
        }
      }
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
    this.toggleZoekenTarget.disabled = false
    this.zoekFieldTarget.focus()
    this.clearSelectedTaakUuidField()
    this.submit()
    this.cancelZoekTarget.classList.add('hide')
    this.zoekButtonTarget.classList.remove('hide')
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
    const zoekValueLength = e.target.value.length
    this.toggleZoekenTarget.disabled = zoekHasValue
    this.cancelZoekTarget.classList[zoekHasValue ? 'remove' : 'add']('hide')
    this.zoekButtonTarget.classList[zoekHasValue ? 'add' : 'remove']('hide')
    this.clearSelectedTaakUuidField()
    if (zoekValueLength === 0 || zoekValueLength > 2) {
      this.submit()
    }
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
      taakAfstand.textContent = ` | ${this.formatDistance(
        Math.round(
          markerLocation.distanceTo([
            this.currentPosition.coords.latitude,
            this.currentPosition.coords.longitude,
          ])
        )
      )}`
    }
  }
  updateTaakAfstandTargets() {
    this.taakAfstandTargets.forEach((elem) => {
      this.taakAfstandTargetConnected(elem)
    })
  }
  onToggleSortingContainer() {
    this.toggleSortViewTarget.parentElement.classList.toggle('show')
  }
  onToggleSearchContainer() {
    if (!this.zoekFieldTarget.value) {
      this.zoekFieldContainerTarget.classList.toggle('hidden-vertical')
      this.zoekFieldContainerTarget.classList.toggle('show-vertical')
      this.zoekFieldDefaultContainerTarget.classList.toggle('hidden-vertical')
      this.zoekFieldDefaultContainerTarget.classList.toggle('show-vertical')

      if (this.zoekFieldContainerTarget.classList.contains('show-vertical')) {
        this.zoekFieldTarget.focus()
      }
      if (
        !this.zoekFieldContainerTarget.classList.contains('show-vertical') &&
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
    // this.element.classList.toggle('showMap')
    this.toggleMapViewTarget.parentElement.classList.toggle('show')
  }

  showMap() {
    this.element.classList.add('showMap')
    this.toggleMapViewTarget.parentElement.classList.toggle('show')
  }

  showList() {
    this.element.classList.remove('showMap')
    this.toggleMapViewTarget.parentElement.classList.toggle('show')
  }

  showFilters() {
    this.element.classList.add('show-filters')
    scrollPositionForDialog = window.scrollY
    document.body.style.top = `-${scrollPositionForDialog}px`
    document.body.style.position = 'fixed'
    this.filtersheetTarget.showModal()
    this.filtersheetTarget.addEventListener('click', (event) => {
      if (event.target === event.currentTarget) {
        event.stopPropagation()
        this.hideFilters()
      }
    })
  }

  hideFilters() {
    this.element.classList.remove('show-filters')
    document.body.style.position = ''
    document.body.style.top = ''
    this.filtersheetTarget.close()
    window.scrollTo({ top: scrollPositionForDialog, left: 0, behavior: 'instant' })
    this.filtersheetTarget.removeEventListener('click', (event) => {
      if (event.target !== this.filtersheetTarget.querySelector('.full-page-view__main')) {
        this.closeInfosheet()
      }
    })
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
    if (km < 99.9) {
      return `${(Math.round(km * 10) / 10).toLocaleString('nl-NL', {
        minimumFractionDigits: 1,
      })} km`
    }
    return `${Math.round(km).toLocaleString('nl-NL')} km`
  }
}
