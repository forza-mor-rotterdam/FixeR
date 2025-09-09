import { Controller } from '@hotwired/stimulus'

let timeoutId = null
export default class extends Controller {
  static showSortingContainer = false
  static showSearchContainer = false
  static sortDirectionReversed = false

  currentPosition = null
  distanceThreshold = 50 // meter
  page = sessionStorage.getItem('page_number') || 1
  lastRefreshPosition = null

  static outlets = ['taken-kaart']
  static targets = ['taakItem', 'containerHeader']
  static values = {
    selectedTaakUuid: String,
  }

  initialize() {
    this.addEventListeners()
  }
  connect() {
    if (this.selectedTaakUuidValue) {
      setTimeout(() => {
        this.selectTaakMarker({
          params: { taakUuid: this.selectedTaakUuidValue, preventScroll: false },
        })
      }, 200)
    }
    document.addEventListener('turbo:before-fetch-response', () => {
      this.setScrollPosition()
    })
  }
  disconnect() {
    if (this.hasTakenKaartOutlet) {
      this.takenKaartOutlet.clearMarkers()
    }
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
        if (frame?.complete) {
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
  addEventListeners() {
    window.addEventListener('closeModal', () => {
      this.setScrollPosition()
    })
  }
  selecteerTaakItem(taakUuid, preventScroll) {
    const taakItemTarget = this.taakItemTargets.find((elem) => elem.dataset.uuid === taakUuid)
    taakItemTarget?.classList.toggle('highlight-once', taakItemTarget.dataset.uuid === taakUuid)
    preventScroll || taakItemTarget?.scrollIntoView()
    setTimeout(() => {
      taakItemTarget?.classList.remove('highlight-once')
    }, 2000)
  }
  deselecteerTaakItem(taakUuid) {
    const taakItemTarget = this.taakItemTargets.find((elem) => elem.dataset.uuid === taakUuid)
    taakItemTarget?.classList.remove('active')
  }
  selectTaakMarker(e) {
    if (this.hasTakenKaartOutlet) {
      const preventScroll = e.params['preventScroll'] != false
      this.takenKaartOutlet.selectTaakMarker(e.params.taakUuid, preventScroll)
    }
  }
  taakItemTargetConnected(taakItem) {
    if (this.hasTakenKaartOutlet) {
      this.takenKaartOutlet.addTaakMarker(taakItem)
    }
  }
  taakItemTargetDisconnected(taakItem) {
    if (this.hasTakenKaartOutlet) {
      this.takenKaartOutlet.clearTaakMarker(taakItem.dataset.uuid)
    }
  }
}
