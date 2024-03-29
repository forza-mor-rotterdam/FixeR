import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

let showSortingContainer = false
let showSearchContainer = false
let sortDirectionReversed = false
let currentPosition = null

export default class extends Controller {
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
    let self = this
    self.page = 1
    self.distanceToLastRefreshPositionTreshold = 50 //meter
    self.lastRefreshPosition = null
    self.element[self.identifier] = self
    self.element.addEventListener('orderChangeEvent', function (e) {
      self.currentOrder = e.detail.order
      self.reloadTakenLijst()
    })
    self.element.addEventListener('searchChangeEvent', function () {
      self.reloadTakenLijst()
    })

    if (self.hasSortingTarget && showSortingContainer === true) {
      self.sortingTarget.classList.remove('hidden-vertical')
      self.sortingTarget.classList.add('show-vertical')
    }

    self.element.addEventListener('markerSelectedEvent', function (e) {
      self.selecteerTaakItem(e.detail.taakId)
    })
    self.element.addEventListener('markerDeselectedEvent', function (e) {
      self.deselecteerTaakItem(e.detail.taakId)
    })
    window.addEventListener('positionChangeEvent', function (e) {
      self.positionWatchSuccess(e.detail.position)
    })
    self.element.addEventListener('kaartModusChangeEvent', function (e) {
      self.kaartOutlet.kaartModusChangeHandler(e.detail.kaartModus, e.detail.requestType)
    })
    let childControllerConnectedEvent = new CustomEvent('childControllerConnectedEvent', {
      bubbles: true,
      cancelable: false,
      detail: {
        controller: self,
      },
    })

    window.dispatchEvent(childControllerConnectedEvent)

    window.addEventListener('childControllerConnectedEvent', function (e) {
      if (e.detail.controller.identifier == 'filter') {
        self.activeFilterCountTarget.textContent = e.detail.controller.activeFilterCountValue
        self.reloadTakenLijst()
      }
    })
  }
  connect() {}
  taakAfstandTargetConnected(element) {
    const markerLocation = new L.LatLng(element.dataset.latitude, element.dataset.longitude)
    element.textContent = Math.round(markerLocation.distanceTo(currentPosition))
  }
  selecteerTaakItem(taakId) {
    let self = this

    for (const taakItemTarget of self.taakItemTargets) {
      if (taakItemTarget.dataset.id == taakId) {
        taakItemTarget.classList.add('selected')
        taakItemTarget.scrollIntoView({
          behavior: 'smooth',
          block: 'end',
          inline: 'nearest',
        })
      } else {
        taakItemTarget.classList.remove('selected')
      }
    }
  }
  deselecteerTaakItem() {
    let self = this
    for (const taakItemTarget of self.taakItemTargets) {
      taakItemTarget.classList.remove('selected')
    }
  }
  positionWatchSuccess(position) {
    let self = this
    currentPosition = [position.coords.latitude, position.coords.longitude]
    if (self.lastRefreshPosition == null) {
      self.lastRefreshPosition = currentPosition
    }
    if (self.hasKaartOutlet) {
      self.kaartOutlet.positionChangeEvent(position)
    }
    if (self.hasTaakAfstandTarget) {
      for (const elem of self.taakAfstandTargets) {
        const markerLocation = new L.LatLng(elem.dataset.latitude, elem.dataset.longitude)
        const afstand = Math.round(markerLocation.distanceTo(currentPosition))
        elem.textContent = afstand
      }
    }
    const lastRefreshLocation = new L.LatLng(
      self.lastRefreshPosition[0],
      self.lastRefreshPosition[1]
    )
    const distanceToLastRefreshPosition = Math.round(
      lastRefreshLocation.distanceTo(currentPosition)
    )
    console.log('distanceToLastRefreshPosition')
    console.log(distanceToLastRefreshPosition)
    if (
      distanceToLastRefreshPosition > self.distanceToLastRefreshPositionTreshold &&
      self.currentOrder == 'Afstand'
    ) {
      self.reloadTakenLijst()
    }
  }
  reloadTakenLijst() {
    let self = this
    let takenLijstElement = self.element.querySelector('#taken_lijst')
    const url = `/taken/lijst/?lat=${currentPosition[0]}&lon=${currentPosition[1]}&page=${self.page}`
    takenLijstElement.setAttribute('src', url)
    takenLijstElement.reload()
  }
  selectTaakMarker(e) {
    let self = this
    self.kaartOutlet.selectTaakMarker(e.params.taakId)
  }
  onPageClickEvent(e) {
    let self = this
    e.preventDefault()
    self.page = e.params.page
    self.reloadTakenLijst()
  }
  taakItemLijstTargetConnected() {
    let self = this
    self.lastRefreshPosition = [currentPosition[0], currentPosition[1]]
    self.takenCountTarget.textContent = self.taakItemLijstTarget.dataset.takenCount
    self.kaartOutlet.clearMarkers()
    let kaartMarkers = []
    for (const taakItem of self.taakItemTargets) {
      if (taakItem.dataset.geometrie != '') {
        kaartMarkers.push({
          geometrie: JSON.parse(taakItem.dataset.geometrie),
          adres: taakItem.dataset.adres,
          afbeeldingUrl: taakItem.dataset.afbeeldingUrl,
          taakId: taakItem.dataset.id,
          titel: taakItem.dataset.titel,
        })
      }
    }
    self.kaartOutlet.plotMarkers(kaartMarkers)
  }
  toggleMapView() {
    this.element.classList.toggle('showMap')
  }
  onToggleSortingContainer() {
    let self = this
    self.sortingTarget.classList.toggle('hidden-vertical')
    self.sortingTarget.classList.toggle('show-vertical')
    showSortingContainer = !showSortingContainer
    sortDirectionReversed = sortDirectionReversed !== undefined
  }

  onToggleSearchContainer() {
    let self = this
    self.searchTarget.classList.toggle('hidden-vertical')
    self.searchTarget.classList.toggle('show-vertical')
    showSearchContainer = !showSearchContainer
  }
}
