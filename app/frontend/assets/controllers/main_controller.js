import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

export default class extends Controller {
  static targets = ['gpsField', 'kaartModusOption', 'sorteerField', 'navigation']
  static outlets = ['taken-kaart', 'taken-overzicht', 'taak-detail']

  initialize() {
    this.takenLijst = null
    this.detail = null
    this.positionWatchOptions = {
      enableHighAccuracy: true,
      timeout: 5000,
      maximumAge: 0,
    }
    this.setNavigatorEventHandlers()

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
  setNavigatorEventHandlers() {
    if (!this.navigatorWatchId) {
      this.navigatorWatchId = navigator.geolocation.watchPosition(
        this.getCurrentPositionSuccess,
        this.positionWatchError,
        this.positionWatchOptions
      )
    }
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
  getCurrentPositionSuccess = (position) => {
    document.body.classList.remove('geolocation-error')

    let distance = 0
    if (this.currentPosition) {
      const myLocation = new L.LatLng(
        this.currentPosition.coords.latitude,
        this.currentPosition.coords.longitude
      )
      distance = myLocation.distanceTo([position.coords.latitude, position.coords.longitude])
    }
    if (!this.currentPosition || distance > 5) {
      console.log(`Afstand tot vorige positie: ${distance}m`)
      this.currentPosition = position
      this.positionWatchSuccess()
    }
  }
  positionWatchSuccess = () => {
    if (this.hasTakenKaartOutlet) {
      this.takenKaartOutlet.positionChangeEvent(this.currentPosition)
    }
    if (this.hasTakenOverzichtOutlet) {
      this.takenOverzichtOutlet.positionChangeEvent(this.currentPosition)
    }
    if (this.hasTaakDetailOutlet) {
      this.taakDetailOutlet.positionChangeEvent(this.currentPosition)
    }
  }
  takenKaartOutletConnected() {
    if (this.currentPosition) {
      this.takenKaartOutlet.positionChangeEvent(this.currentPosition)
    }
  }
  takenOverzichtOutletConnected() {
    if (this.currentPosition) {
      this.takenOverzichtOutlet.positionChangeEvent(this.currentPosition)
    }
  }
  taakDetailOutletConnected() {
    if (this.currentPosition) {
      this.taakDetailOutlet.positionChangeEvent(this.currentPosition)
    }
  }
  positionPermissionState(permissionEnable) {
    const afstandOption = this.sorteerFieldTarget.querySelector('option[value="Afstand"]')
    this.kaartModusOptionTargets
      .find((elem) => elem.value === 'volgen')
      ?.closest('li')
      .classList[permissionEnable ? 'remove' : 'add']('disabled')
    if (this.hasSorteerFieldTarget && afstandOption) {
      afstandOption.disabled = !permissionEnable
    }
    if (!permissionEnable) {
      if (this.hasKaartModusOptionTarget) {
        this.element.querySelector(`input[name="${this.kaartModusOptionTarget.name}"]`).value =
          'toon_alles'
      }
      const template = document.getElementById('template_snack_geen_locatie')
      const clone = template?.content.cloneNode(true)
      const snackContainer = document.getElementById('snack_lijst')
      snackContainer?.appendChild(clone)
    }
  }
  positionWatchError = (error) => {
    console.log('positionWatchError: ', error)
    document.body.classList.add('geolocation-error')

    const errorCodeExplanation = {
      1: 'Je hebt locatie bepaling voor FixeR uit staan. Ga naar de locatie instellingen van je browser om deze aan te zetten!',
      2: 'Zit je soms in de put!',
      3: 'Het bepalen van je locatie duurt te lang!',
      4: 'Locatie fout!',
    }
    console.log(errorCodeExplanation[error.code])

    switch (error.code) {
      case error.PERMISSION_DENIED:
        setTimeout(() => {
          this.positionPermissionState(false)
        }, 1000)
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
    if (this.hasTakenOverzichtOutlet) {
      this.takenOverzichtOutlet.positionWatchError(error.code)
    }
  }
  openNavigation() {
    if (this.hasNavigationTarget) {
      document.body.classList.add('show-navigation')
      this.navigationTarget.classList.add('show')
    }
  }
  closeNavigation() {
    if (this.hasNavigationTarget) {
      document.body.classList.remove('show-navigation')
      this.navigationTarget.classList.remove('show')
    }
  }
}
