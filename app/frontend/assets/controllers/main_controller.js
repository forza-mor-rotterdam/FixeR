import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

export default class extends Controller {
  static targets = ['gpsField', 'takenKaart']
  static outlets = ['taken']

  initialize() {
    this.incidentlist = null
    this.detail = null

    navigator.geolocation.getCurrentPosition(
      this.getCurrentPositionSuccess,
      this.positionWatchError
    )

    window.addEventListener(
      'childControllerConnectedEvent',
      this.childControllerConnectedEventHandler
    )

    this.toastTurboFrame = document.getElementById('tf_toast_lijst')
    this.sessionTimerTurboFrame = document.getElementById('tf_session_timer')
    this.notificationsTurboFrameReloadTimeout = null

    setTimeout(() => {
      document.addEventListener('turbo:fetch-request-error', (event) => {
        event.preventDefault()
        window.location.replace(`/login/?next=${document.location.pathname}`)
      })
      document.addEventListener('turbo:frame-load', (event) => {
        if (![this.toastTurboFrame, this.sessionTimerTurboFrame].includes(event.target)) {
          this.reloadNotificationsTurboFrame()
        }
      })
    }, 1000)
    document.addEventListener('turbo:frame-missing', (event) => {
      const {
        detail: { response, visit },
      } = event
      console.log(response)
      console.log(event)
      event.preventDefault()
      // visit(document.location.href)

      console.error('Content missing', response.url, visit)
      if (![this.toastTurboFrame, this.sessionTimerTurboFrame].includes(event.target)) {
        this.reloadNotificationsTurboFrame()
      }
    })
  }
  reloadNotificationsTurboFrame() {
    if (!this.notificationsTurboFrameReloadTimeout) {
      this.notificationsTurboFrameReloadTimeout = setTimeout(() => {
        try {
          this.toastTurboFrame?.reload()
          this.sessionTimerTurboFrame?.reload()
          this.notificationsTurboFrameReloadTimeout = null
        } catch (e) {
          console.error('reloadNotificationsTurboFrame error: ', e)
        }
      }, 200)
    }
  }
  takenKaartTargetConnected(takenKaart) {
    console.log('takenKaart')
    console.log(takenKaart)
  }
  connect() {
    console.log('CONNECT MAIN, removing selectedTaakId from sessionStorage')
    sessionStorage.removeItem('selectedTaakId')
  }

  childControllerConnectedEventHandler = (e) => {
    if (e.detail.controller.identifier === 'incidentlist') {
      this.incidentlist = e.detail.controller
      // this.incidentlist.positionWatchSuccess(this.currentPosition)
    }
    if (e.detail.controller.identifier === 'detail') {
      this.detail = e.detail.controller
      // this.detail.positionWatchSuccess(this.currentPosition)
    }
  }

  getCurrentPositionSuccess = (position) => {
    document.body.classList.remove('geolocation-error')
    console.log('getCurrentPositionSuccess')

    let distance = null
    if (this.currentPosition) {
      const myLocation = new L.LatLng(
        this.currentPosition.coords.latitude,
        this.currentPosition.coords.longitude
      )
      distance = myLocation.distanceTo([position.coords.latitude, position.coords.longitude])
    }
    if (!distance || distance > 5) {
      this.currentPosition = position
      this.gpsFieldTarget.value = `${this.currentPosition.coords.latitude},${this.currentPosition.coords.longitude}`
      this.positionWatchSuccess()
    }
  }

  positionWatchSuccess = () => {
    this.takenKaartTarget?.takenKaart?.positionChangeEvent(this.currentPosition)
    this.detail?.positionWatchSuccess(this.currentPosition)
  }
  positionWatchError = (error) => {
    console.log('positionWatchError: ', error)
    document.body.classList.remove('geolocation-error')

    const errorCodeExplanation = {
      1: 'Je hebt locatie bepaling voor FixeR uit staan. Ga naar de locatie instellingen van je browser om deze aan te zetten!',
      2: 'Zit je soms in de put!',
      3: 'Het bepalen van je locatie duurt te lang!',
      4: 'Locatie fout!',
    }
    console.log(errorCodeExplanation)

    switch (error.code) {
      case error.PERMISSION_DENIED:
        console.log('User denied the request for Geolocation.')
        break
      case error.POSITION_UNAVAILABLE:
        console.log('Location information is unavailable.')
        break
      case error.TIMEOUT:
        console.log('The request to get user location timed out.')
        break
      case error.UNKNOWN_ERROR:
        console.log('An unknown error occurred.')
        break
    }
  }

  showFilters() {
    document.body.classList.add('show-filters')
    // used for scrolling to last selected task
    sessionStorage.removeItem('selectedTaakId')
  }

  hideFilters() {
    document.body.classList.remove('show-filters')
  }
}
