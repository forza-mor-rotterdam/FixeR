import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

let timeoutId = null
export default class extends Controller {
  static showSortingContainer = false
  static showSearchContainer = false
  static sortDirectionReversed = false

  currentPosition = null
  distanceThreshold = 50 // meter
  page = sessionStorage.getItem('page_number') || 1
  lastRefreshPosition = null

  static outlets = ['takenKaart']
  static targets = [
    'sorting',
    'search',
    'toggleMapView',
    'taakAfstand',
    'taakItem',
    'taakItemLijst',
    'activeFilterCount',
    'takenCount',
    'incidentlist',
    'containerHeader',
  ]

  initialize() {
    this.addEventListeners()
    window.dispatchEvent(
      new CustomEvent('childControllerConnectedEvent', {
        bubbles: true,
        cancelable: false,
        detail: { controller: this },
      })
    )
  }

  connect() {
    document.addEventListener('turbo:before-fetch-response', () => {
      this.setScrollPosition()
    })
  }

  disconnect() {
    document.removeEventListener('turbo:before-fetch-response', this.setScrollPosition)
    clearTimeout(timeoutId)
  }

  setScrollPosition() {
    if (!document.body.classList.contains('show-modal')) {
      if (this.hasIncidentlistTarget) {
        const frame = this.incidentlistTarget.querySelector('turbo-frame')
        const scrollTarget =
          window.innerWidth < 1024 ? document.documentElement : this.incidentlistTarget
        const scrollCorrection =
          window.innerWidth < 1024
            ? document.querySelector('main').offsetTop +
              this.containerHeaderTarget.clientHeight +
              this.element.offsetHeight / 2
            : this.element.offsetHeight / 2
        if (frame.complete) {
          timeoutId = setTimeout(() => {
            const activeItem = this.element.querySelector(
              `[data-uuid="${sessionStorage.getItem('selectedTaakId')}"]`
            )
            if (activeItem) {
              const topPos = activeItem.offsetTop + activeItem.offsetHeight
              scrollTarget.scrollTop = topPos - scrollCorrection
            }
          }, 100)
        }
      }
    }
  }

  waitForElm(selector) {
    return new Promise((resolve) => {
      if (document.querySelector(selector)) {
        return resolve(document.querySelector(selector))
      }

      const observer = new MutationObserver(() => {
        if (document.querySelector(selector)) {
          observer.disconnect()
          resolve(document.querySelector(selector))
        }
      })

      // If you get "parameter 1 is not of type 'Node'" error, see https://stackoverflow.com/a/77855838/492336
      observer.observe(document.body, {
        childList: true,
        subtree: true,
      })
    })
  }

  addEventListeners() {
    this.element.addEventListener('orderChangeEvent', (e) => this.orderChangeHandler(e))
    this.element.addEventListener('searchChangeEvent', () => this.reloadTakenLijst())
    this.element.addEventListener('markerSelectedEvent', (e) =>
      this.selecteerTaakItem(e.detail.taakId)
    )
    this.element.addEventListener('markerDeselectedEvent', () => this.deselecteerTaakItem())
    window.addEventListener('positionChangeEvent', (e) =>
      this.positionWatchSuccess(e.detail.position)
    )
    this.element.addEventListener('kaartModusChangeEvent', (e) => this.kaartModusChangeHandler(e))
    window.addEventListener('closeModal', () => {
      this.setScrollPosition()
    })
  }

  selecteerTaakItem(taakId) {
    // map related
    sessionStorage.setItem('selectedTaakId', taakId)
    this.taakItemTargets.forEach((taakItemTarget) => {
      taakItemTarget.classList.toggle('highlight-once', taakItemTarget.dataset.uuid === taakId)
      if (taakItemTarget.dataset.uuid === taakId) {
        //scroll to this element
        const scrollTarget =
          window.innerWidth < 1024 ? document.documentElement : this.incidentlistTarget
        const scrollCorrection =
          window.innerWidth < 1024
            ? document.querySelector('main').offsetTop +
              this.containerHeaderTarget.clientHeight +
              this.element.offsetHeight / 2
            : this.element.offsetHeight / 2
        const topPos = taakItemTarget.offsetTop + taakItemTarget.offsetHeight
        scrollTarget.scrollTop = topPos - scrollCorrection
      }
      setTimeout(() => {
        taakItemTarget.classList.remove('highlight-once')
      }, 2000)
    })
  }

  deselecteerTaakItem() {
    // map related
    if (!document.body.classList.contains('show-modal')) {
      this.taakItemTargets.forEach((taakItemTarget) => {
        taakItemTarget.classList.remove('active')
      })
    }
  }

  taakAfstandTargetConnected(element) {
    if (this.currentPosition) {
      const markerLocation = new L.LatLng(element.dataset.latitude, element.dataset.longitude)
      element.textContent = Math.round(markerLocation.distanceTo(this.currentPosition))
    }
  }

  selectTaakMarker(e) {
    this.takenKaartOutlet.selectTaakMarker(e.params.taakId)
  }

  positionWatchSuccess(position) {
    console.log('INCIDENT LIST: positionWatchSuccess')
    this.currentPosition = [position.coords.latitude, position.coords.longitude]
    if (!this.lastRefreshPosition) {
      this.lastRefreshPosition = [...this.currentPosition]
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
    const lastRefreshLocation = new L.LatLng(...this.lastRefreshPosition)
    const distanceToLastRefreshPosition = Math.round(
      lastRefreshLocation.distanceTo(this.currentPosition)
    )

    if (distanceToLastRefreshPosition > this.distanceThreshold && this.currentOrder === 'Afstand') {
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
    // this.lastRefreshPosition = [...this.currentPosition]
    this.takenCountTarget.textContent = this.taakItemLijstTarget.dataset.takenCount
    console.log('taakItemLijstTargetConnected')
    this.takenKaartOutlet?.clearMarkers()
    const kaartMarkers = this.getKaartMarkers()
    this.takenKaartOutlet?.plotMarkers(kaartMarkers)
  }

  getKaartMarkers() {
    const kaartMarkers = []
    this.taakItemTargets.forEach((taakItem) => {
      if (taakItem.dataset.geometrie) {
        kaartMarkers.push({
          geometrie: JSON.parse(taakItem.dataset.geometrie),
          adres: taakItem.dataset.adres,
          afbeeldingUrl: taakItem.dataset.afbeeldingUrl,
          taakId: taakItem.dataset.uuid,
          titel: taakItem.dataset.titel,
          hasRemark: taakItem.dataset.hasRemark,
        })
      }
    })
    return kaartMarkers
  }

  toggleMapView() {
    this.element.classList.toggle('showMap')
    this.setScrollPosition()
  }

  onToggleSortingContainer() {
    this.sortingTarget.classList.toggle('hidden-vertical')
    this.sortingTarget.classList.toggle('show-vertical')
    // this.constructor.showSortingContainer = !this.constructor.showSortingContainer
    // this.constructor.sortDirectionReversed = this.constructor.sortDirectionReversed !== undefined
  }

  onToggleSearchContainer() {
    this.searchTarget.classList.toggle('hidden-vertical')
    this.searchTarget.classList.toggle('show-vertical')
    if (this.searchTarget.classList.contains('hidden-vertical')) {
      let myEvent = new Event('clearSearchForTasks', {
        bubbles: true,
        cancelable: false,
      })
      window.dispatchEvent(myEvent)
    }
    this.constructor.showSearchContainer = !this.constructor.showSearchContainer
  }
}
