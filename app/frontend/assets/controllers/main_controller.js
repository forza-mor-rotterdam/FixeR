import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

let currentPosition = { coords: { latitude: 51.9247772, longitude: 4.4780972 } }
let incidentlist = null
let detail = null

let kaartModus = null
let kaartStatus = null

export default class extends Controller {
  static outlets = ['taken']

  initialize() {
    let self = this
    self.element[self.identifier] = self
    const status = {
      zoom: 16,
      center: [currentPosition.coords.latitude, currentPosition.coords.longitude],
    }
    kaartModus = 'volgen'
    kaartStatus = {
      volgen: status,
      toon_alles: status,
    }
    if (!sessionStorage.getItem('kaartStatus')) {
      sessionStorage.setItem('kaartStatus', JSON.stringify(kaartStatus))
    }

    navigator.geolocation.getCurrentPosition(
      self.getCurrentPositionSuccess.bind(self),
      self.positionWatchError.bind(self)
    )
    window.addEventListener('childControllerConnectedEvent', function (e) {
      if (e.detail.controller.identifier == 'incidentlist') {
        incidentlist = e.detail.controller
        incidentlist.positionWatchSuccess(currentPosition)
      }
      if (e.detail.controller.identifier == 'detail') {
        detail = e.detail.controller
        detail.positionWatchSuccess(currentPosition)
      }
    })
  }
  connect() {}
  getCurrentPositionSuccess(position) {
    let self = this
    self.positionWatchSuccess(position)
  }
  positionWatchSuccess(position) {
    const myLocation = new L.LatLng(
      currentPosition.coords.latitude,
      currentPosition.coords.longitude
    )
    const distance = myLocation.distanceTo([position.coords.latitude, position.coords.longitude])
    if (distance > 5) {
      currentPosition = position
      if (incidentlist) {
        incidentlist.positionWatchSuccess(position)
      }
      if (detail) {
        detail.positionWatchSuccess(position)
      }
    }
  }
  positionWatchError(error) {
    let self = this
    console.log('positionWatchError controller id:', self.identifier)
    console.log('handleNoCurrentLocation, error: ', error)
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
    self.getCurrentPositionSuccess(currentPosition)
  }
  showFilters() {
    document.body.classList.add('show-filters')
  }

  hideFilters() {
    document.body.classList.remove('show-filters')
  }
  setKaartModus(_kaartModus) {
    kaartModus = _kaartModus
  }
  getCurrentPosition() {
    return currentPosition
  }
  getKaartModus() {
    return kaartModus
  }
  setKaartStatus(_kaartStatus) {
    kaartStatus[kaartModus] = _kaartStatus
    let sessionState = JSON.parse(sessionStorage.getItem('kaartStatus'))
    sessionState[kaartModus] = _kaartStatus
    const sessionStateString = JSON.stringify(sessionState)
    sessionStorage.setItem('kaartStatus', sessionStateString)
  }
  getKaartStatus() {
    const sessionState = JSON.parse(sessionStorage.getItem('kaartStatus'))
    return sessionState[kaartModus]
  }
}
