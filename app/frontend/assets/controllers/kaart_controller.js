import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

let markerIcon,
  markerBlue,
  markerMagenta = null
let markerMe = null
let mapDiv = null
let map = null
const url =
  'https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{layerName}/{crs}/{z}/{x}/{y}.{format}'
let buurten = null

export default class extends Controller {
  static outlets = ['main']
  initialize() {
    let self = this
    markerMe = null
    self.markerList = []
    self.element[self.identifier] = self

    mapDiv = document.getElementById('incidentMap')
    map = L.map('incidentMap', self.mainOutlet.getKaartStatus())
    if (mapDiv) {
      this.drawMap()
    }

    map.on('moveend', () => {
      self.mainOutlet.setKaartStatus({
        zoom: map.getZoom(),
        center: map.getCenter(),
      })
    })
    map.on('zoomend', () => {
      self.mainOutlet.setKaartStatus({
        zoom: map.getZoom(),
        center: map.getCenter(),
      })
    })
    map.on('popupopen', ({ popup }) => {
      if (popup instanceof L.Popup) {
        const marker = popup._source
        let markerSelectedEvent = new CustomEvent('markerSelectedEvent', {
          bubbles: true,
          cancelable: false,
          detail: { taakId: marker.options.taakId },
        })
        self.element.dispatchEvent(markerSelectedEvent)
      }
    })
    map.on('popupclose', ({ popup }) => {
      if (popup instanceof L.Popup) {
        const marker = popup._source
        let markerSelectedEvent = new CustomEvent('markerDeselectedEvent', {
          bubbles: true,
          cancelable: false,
          detail: { taakId: marker.options.taakId },
        })
        self.element.dispatchEvent(markerSelectedEvent)
      }
    })
  }
  kaartModusChangeHandler(_kaartModus) {
    let self = this
    if (!markerMe) {
      return
    }
    self.mainOutlet.setKaartModus(_kaartModus)
    switch (_kaartModus) {
      case 'volgen':
        map.flyTo(markerMe.getLatLng(), self.mainOutlet.getKaartStatus().zoom)
        break

      case 'toon_alles':
        map.fitBounds(self.markers.getBounds())
        break
    }
  }
  positionChangeEvent(position) {
    let self = this
    if (!markerMe) {
      markerMe = new L.Marker([position.coords.latitude, position.coords.longitude], {
        icon: markerBlue,
      })
      self.markers.addLayer(markerMe)
    } else {
      markerMe.setLatLng([position.coords.latitude, position.coords.longitude])
    }
    if (self.mainOutlet.getKaartModus() == 'volgen') {
      map.setView(markerMe.getLatLng(), self.mainOutlet.getKaartStatus().zoom)
    }
  }

  disconnect() {}

  onTwoFingerDrag(event) {
    if (event.type === 'touchstart' && event.touches.length === 1) {
      event.currentTarget.classList.add('swiping')
    } else {
      event.currentTarget.classList.remove('swiping')
    }
  }

  selectTaakMarker(taakId) {
    let self = this
    let obj = self.markerList.find((obj) => obj.options.taakId == taakId)
    obj.openPopup()
  }

  drawMap() {
    let self = this
    markerIcon = L.Icon.extend({
      options: {
        iconSize: [36, 36],
        iconAnchor: [18, 30],
        popupAnchor: [0, -7],
      },
    })

    markerBlue = new markerIcon({
      iconSize: [26, 26],
      iconAnchor: [13, 13],
      iconUrl:
        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAATESURBVHgBrVZNTGNVFL7vp9AfCB0mpAOSoRgdGUQcI8yiCYImGjXExBBYGbshcdGiKxHHhSVRdG+M0YWrccUC4qSz0EQT2RATiNHEBFKcjnYmg6BtLfa/7/qdx72vr50OU+qc5OTed9895zvn3HPOvYw1SZxzL/gt8Br4Bq8Szb8HB8F+9qAolUqdgcIIOMmbowj7vwQlg3XeNUu/5XK5wZN0Kw3AFBCDoN/pdH6HJb/8t3GTsWu7nEV3GbuZOl4b9TH2BPjKhMIGvDWqboCfA8dJ34nAApRjqmK+J0FTecY+2uDs0x/ZiRS6fGxAl7MKnkgkxvr7+5NCr0VqjRX4GYlE1Eql8r4d9KWr9wcloj0vY286by0N9vX1vWl6A6dqsOpkFSTTw11dXTG58M63zYHaKQzPP37eUp3c2tq6MDY29hfmltdqnRGqw+F4Vi7QOZ4WlIhkKB8EeUdGRoICS7kncFtb2+tyYWWDs1aIpKK7lqyiadpkQ2ARf2JdVdUB+fOXO6xlurZTnUPnaG9vr+Mu4OXlZWV4eFjr7u52YNN5+fPnP1nL9Hu6Bvh8qVTSCENiKjYD2sAueP+3FOj4sLVQS8WZ9ywHqU7P+v3+3Pj4eGl1dbVios/OziqoNaWzs1ODZQm5e6CLtUzUVCShPP/AoMbjcRWg5poJjA+lUChomUxGQ8f6VQpMX2At06gNGLpvsWpyKcz2wQ4ODszF/f19q4CmH1NYK0RS7z5TDXMsFltj1WO1gPnU1BTr6emhA+VLS0trCE2Gfk4gv0Pj7NQUuqzUHNP6+jo5owDDArfqGJlnAkej0X9g4Vdy/Qosf9LHmiYK8dJE9XtnZ+fzlZWVREdHh0HfcNLEMYEnJycNAWwg+yoLCwtX8/n8bfpHDf/6awoLjze4yhp4Snu94pKgsx0aGvoMo3F0dGTgOI16GTKAtp/BVUh1/Hg4HH4FiXbLfsnGU5y/8bXBA18Y3PPBMQ9/YvC3vzH4D/HaC5lkQ6HQNDrhsMvl6odOL8rJSZeQHZicoTruBJ9rb29/FOOl+fn5V7PZ7G1+SiIZkkXfvwQ9j4B9ON8OgXFX4DS0NTdq+SzmA7D0IsYxcGB7e/tL6DPuB4gekKG9gUDgBYA+DdmLIoLdYBdhSGClLtw6uB3shoDHMAw39FE3cwSDwYdmZmaeQud50ePxnEP4ekkIIb2TTCZje3t7Py0uLl7f3NxMAxQ2lHL4nQX/K8YCuMTE1VgtNlwUc3Nz1Fl0r9frKhaLLoTMTUZAERmjQ5nOqjcayXJd15VyuUxJw7GvjLGMfQSSdbvdWSICRXc0W6X9bOvPmsLhEMnmFCFyQmmbBCcwKQtQGgi4QsAClN4gOTwo8um0+R4hTyvM9hDQ2L3J9AJhNaDMIAKggeZSxrQCNkehlDiP7zyOIIfkzEEmjzIqoG5L6NGGHbSRx5JUVj1zh2DTY5y9jhrXoFyFXtNArBlYq8DIIi79IhKzdHh4SMaUpQPNAtuvS4qKhnKgm0vHm0yzGcbRkTiaAxehLKNWyUOaUxUY9a/LZsl8Dglw8tiJ65PO3CPZ5/N5qAzZcT44RJTU+ldlS0RKhCIz/Dg3XY7IVjMiYrSSrhmPWqFGcqcK6X9czfgLQYqNowAAAABJRU5ErkJggg==',
    })
    markerMagenta = new markerIcon({
      iconUrl:
        'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMy43NzgzIDYuMjI0MTJDMTkuNTAwMyAxLjk0NjEzIDEyLjQ5OTkgMS45NDYxMyA4LjIyMTkzIDYuMjI0MTJDMy45NDM5MyAxMC41MDIxIDMuOTQzOTMgMTcuNTAyNSA4LjIyMTkzIDIxLjc4MDVMMTYuMDAwMSAyOS41NTg2TDIzLjc3ODMgMjEuNzgwNUMyOC4wNTYzIDE3LjUwMjUgMjguMDU2MyAxMC41MDIxIDIzLjc3ODMgNi4yMjQxMlpNMTYuMDAwMSAxOC4wMDIzQzE4LjIwOTIgMTguMDAyMyAyMC4wMDAxIDE2LjIxMTQgMjAuMDAwMSAxNC4wMDIzQzIwLjAwMDEgMTEuNzkzMiAxOC4yMDkyIDEwLjAwMjMgMTYuMDAwMSAxMC4wMDIzQzEzLjc5MSAxMC4wMDIzIDEyLjAwMDEgMTEuNzkzMiAxMi4wMDAxIDE0LjAwMjNDMTIuMDAwMSAxNi4yMTE0IDEzLjc5MSAxOC4wMDIzIDE2LjAwMDEgMTguMDAyM1oiIGZpbGw9IiNDOTM2NzUiLz4KPC9zdmc+Cg==',
    })

    let config = {
      crs: 'EPSG:3857',
      format: 'png',
      name: 'standaard',
      layerName: 'standaard',
      type: 'wmts',
      minZoom: 10,
      maxZoom: 19,
      tileSize: 256,
      attribution: '',
      gestureHandling: true,
    }

    L.tileLayer(url, config).addTo(map)

    const resizeObserver = new ResizeObserver(() => {
      map.invalidateSize()

      let markerSelectedEvent = new CustomEvent('markerDeselectedEvent', {
        bubbles: true,
        cancelable: false,
        detail: {},
      })
      self.element.dispatchEvent(markerSelectedEvent)
      map.closePopup()
    })

    resizeObserver.observe(mapDiv)

    //create the marker group
    self.markers = new L.featureGroup()
    //add the markers to the map
    map.addLayer(self.markers)
    //fit the map to the markers

    buurten = L.tileLayer.wms(
      'https://service.pdok.nl/cbs/wijkenbuurten/2022/wms/v1_0?request=GetCapabilities&service=WMS',
      {
        layers: 'buurten',
        format: 'image/png',
        transparent: true,
        minZoom: 10,
        maxZoom: 19,
        srsName: 'EPSG:4326',
        bbox: '51.9247770, 4.4780970, 51.9247774, 4.4780974',
      }
    )
  }

  toggleBuurten() {
    const checkbox = document.getElementById('buurten-checkbox')
    const button = document.getElementById('buurten-button')

    checkbox.checked = !checkbox.checked

    if (checkbox.checked) {
      buurten.addTo(map)
    } else {
      map.removeLayer(buurten)
    }

    button.classList.toggle('active', checkbox.checked)
    checkbox.classList.toggle('active', checkbox.checked)
  }

  makeRoute(event) {
    // let routeUrl = "https://www.google.com/maps/dir"
    // let routeUrl = 'https://www.waze.com/ul?ll=40.75889500,-73.98513100&navigate=yes&zoom=17'
    let routeUrl = 'https://www.waze.com/ul?ll='

    function getRoute(event) {
      let lat = event.params.lat
      let long = event.params.long
      routeUrl += `${lat},${long}&navigate=yes`
      window.open(routeUrl, '_blank')
    }

    getRoute(event)
  }
  clearMarkers() {
    let self = this
    self.markerList = []
    self.markers.clearLayers()
    self.markers.addLayer(markerMe)
  }
  plotMarkers(coordinatenlijst) {
    let self = this

    if (coordinatenlijst) {
      for (const coord of coordinatenlijst) {
        const lat = coord.geometrie.coordinates ? coord.geometrie.coordinates[1] : 51.9247772
        const long = coord.geometrie.coordinates ? coord.geometrie.coordinates[0] : 4.4780972
        const adres = coord.adres
        const afbeelding = coord.afbeeldingUrl
        const titel = coord.titel
        const taakId = coord.taakId

        const markerLocation = new L.LatLng(lat, long)

        const marker = new L.Marker(markerLocation, {
          icon: markerMagenta,
          taakId: taakId,
        })

        const paragraphDistance = `<p>Afstand: <span data-incidentlist-target="taakAfstand" data-latitude="${lat}" data-longitude="${long}"></span> meter</p>`

        const anchorDetail = `<a href="/taak/${taakId}" target="_top" aria-label="Bekijk taak ${taakId}">Details</a>`
        const anchorNavigeer = `<span class="link" data-action="click->kaart#makeRoute" data-kaart-lat-param="${lat}" data-kaart-long-param="${long}" target="_top" aria-label="Navigeer naar taak ${taakId}">Navigeren</span>`
        const divDetailNavigeer = `<div class="display-flex gap">${anchorDetail} | ${anchorNavigeer}</div>`

        let popupContent = `<div></div><div class="container__content"><h5 class="no-margin">${adres}</h5><p>${titel}</p>${paragraphDistance}${divDetailNavigeer}</div>`

        if (afbeelding) {
          popupContent = `<div class="container__image"><img src=${afbeelding}></div><div class="container__content"><h5 class="no-margin">${adres}</h5><p>${titel}</p>${paragraphDistance}${divDetailNavigeer}</div>`
        }

        marker.bindPopup(popupContent, { maxWidth: 460 })

        self.markers.addLayer(marker)
        self.markerList.push(marker)
      }
    }
  }
}
