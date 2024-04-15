import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

export default class extends Controller {
  static showSortingContainer = false
  static showSearchContainer = false
  static sortDirectionReversed = false

  currentPosition = null
  distanceToLastRefreshPositionThreshold = 50 // meter
  page = sessionStorage.getItem('page_number') || 1
  lastRefreshPosition = null

  static outlets = ['kaart']
  static targets = [
    'sorting',
    'search',
    'toggleMapView',
    'taakAfstand',
    'taakItem',
    'taakItemLijst',
    'activeFilterCount',
    'takenCount',
  ]

  initialize() {
    this.addEventListeners()
    this.handleInitialDisplay()

    window.dispatchEvent(
      new CustomEvent('childControllerConnectedEvent', {
        bubbles: true,
        cancelable: false,
        detail: { controller: this },
      })
    )

    window.addEventListener(
      'childControllerConnectedEvent',
      this.childControllerConnectedHandler.bind(this)
    )
  }

  addEventListeners() {
    this.element.addEventListener('orderChangeEvent', this.orderChangeHandler.bind(this))
    this.element.addEventListener('searchChangeEvent', this.reloadTakenLijst.bind(this))
    this.element.addEventListener('markerSelectedEvent', this.selecteerTaakItem.bind(this))
    this.element.addEventListener('markerDeselectedEvent', this.deselecteerTaakItem.bind(this))
    window.addEventListener('positionChangeEvent', this.positionWatchSuccess.bind(this))
    this.element.addEventListener('kaartModusChangeEvent', this.kaartModusChangeHandler.bind(this))
  }

  handleInitialDisplay() {
    if (this.constructor.showSortingContainer) {
      this.showSortingContainer()
    }
  }

  selecteerTaakItem(taakId) {
    this.taakItemTargets.forEach((taakItemTarget) => {
      taakItemTarget.classList.toggle('selected', taakItemTarget.dataset.id === taakId)
    })
  }

  deselecteerTaakItem() {
    this.taakItemTargets.forEach((taakItemTarget) => {
      taakItemTarget.classList.remove('selected')
    })
  }

  taakAfstandTargetConnected(element) {
    const markerLocation = new L.LatLng(element.dataset.latitude, element.dataset.longitude)
    element.textContent = Math.round(markerLocation.distanceTo(this.currentPosition))
  }

  selectTaakMarker(e) {
    this.kaartOutlet.selectTaakMarker(e.params.taakId)
  }

  positionWatchSuccess(position) {
    this.currentPosition = [position.coords.latitude, position.coords.longitude]
    if (!this.lastRefreshPosition) {
      this.lastRefreshPosition = this.currentPosition
    }
    if (this.hasKaartOutlet) {
      this.kaartOutlet.positionChangeEvent(position)
    }
    if (this.hasTaakAfstandTarget) {
      this.updateTaakAfstandTargets()
    }
    this.checkRefreshPositionDistance()
  }

  updateTaakAfstandTargets() {
    this.taakAfstandTargets.forEach((elem) => {
      const markerLocation = new L.LatLng(elem.dataset.latitude, elem.dataset.longitude)
      elem.textContent = Math.round(markerLocation.distanceTo(this.currentPosition))
    })
  }

  checkRefreshPositionDistance() {
    const lastRefreshLocation = new L.LatLng(
      this.lastRefreshPosition[0],
      this.lastRefreshPosition[1]
    )
    const distanceToLastRefreshPosition = Math.round(
      lastRefreshLocation.distanceTo(this.currentPosition)
    )

    if (
      distanceToLastRefreshPosition > this.distanceToLastRefreshPositionThreshold &&
      this.currentOrder === 'Afstand'
    ) {
      this.reloadTakenLijst()
    }
  }

  reloadTakenLijst() {
    const takenLijstElement = document.getElementById('taken_lijst')
    const url = `/taken/lijst/?lat=${this.currentPosition[0]}&lon=${this.currentPosition[1]}&page=${this.page}`
    takenLijstElement.src = url
  }

  onPageClickEvent(e) {
    e.preventDefault()
    this.page = e.params.page
    this.reloadTakenLijst()
  }

  taakItemLijstTargetConnected() {
    this.lastRefreshPosition = [this.currentPosition[0], this.currentPosition[1]]
    this.takenCountTarget.textContent = this.taakItemLijstTarget.dataset.takenCount
    this.kaartOutlet.clearMarkers()
    const kaartMarkers = this.getKaartMarkers()
    this.kaartOutlet.plotMarkers(kaartMarkers)
  }

  getKaartMarkers() {
    const kaartMarkers = []
    this.taakItemTargets.forEach((taakItem) => {
      if (taakItem.dataset.geometrie) {
        kaartMarkers.push({
          geometrie: JSON.parse(taakItem.dataset.geometrie),
          adres: taakItem.dataset.adres,
          afbeeldingUrl: taakItem.dataset.afbeeldingUrl,
          taakId: taakItem.dataset.id,
          titel: taakItem.dataset.titel,
        })
      }
    })
    return kaartMarkers
  }

  toggleMapView() {
    this.element.classList.toggle('showMap')
  }

  onToggleSortingContainer() {
    this.sortingTarget.classList.toggle('hidden-vertical')
    this.sortingTarget.classList.toggle('show-vertical')
    this.constructor.showSortingContainer = !this.constructor.showSortingContainer
    this.constructor.sortDirectionReversed = this.constructor.sortDirectionReversed !== undefined
  }

  onToggleSearchContainer() {
    this.searchTarget.classList.toggle('hidden-vertical')
    this.searchTarget.classList.toggle('show-vertical')
    this.constructor.showSearchContainer = !this.constructor.showSearchContainer
  }

  orderChangeHandler(e) {
    this.currentOrder = e.detail.order
    this.reloadTakenLijst()
  }

  kaartModusChangeHandler(e) {
    this.kaartOutlet.kaartModusChangeHandler(e.detail.kaartModus, e.detail.requestType)
  }

  childControllerConnectedHandler(e) {
    if (e.detail.controller.identifier === 'filter') {
      this.activeFilterCountTarget.textContent = e.detail.controller.activeFilterCountValue
      this.reloadTakenLijst()
    }
  }
}
