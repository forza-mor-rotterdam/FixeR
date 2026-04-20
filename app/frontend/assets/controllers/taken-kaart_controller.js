import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'
const KaartModus = Object.freeze({
  TOON_ALLES: 'toon_alles',
  VOLGEN: 'volgen',
})
const StandaardKaartCenter = { coords: { latitude: 51.9247772, longitude: 4.4780972 } }
const StandaardKaartZoom = 18

export default class MapController extends Controller {
  static outlets = ['taken-lijst', 'taken-overzicht']
  static targets = ['taakPopup', 'taakAfstand']

  static createMarkerIcons = () => ({
    blue: L.icon({
      iconUrl:
        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAATESURBVHgBrVZNTGNVFL7vp9AfCB0mpAOSoRgdGUQcI8yiCYImGjXExBBYGbshcdGiKxHHhSVRdG+M0YWrccUC4qSz0EQT2RATiNHEBFKcjnYmg6BtLfa/7/qdx72vr50OU+qc5OTed9895zvn3HPOvYw1SZxzL/gt8Br4Bq8Szb8HB8F+9qAolUqdgcIIOMmbowj7vwQlg3XeNUu/5XK5wZN0Kw3AFBCDoN/pdH6HJb/8t3GTsWu7nEV3GbuZOl4b9TH2BPjKhMIGvDWqboCfA8dJ34nAApRjqmK+J0FTecY+2uDs0x/ZiRS6fGxAl7MKnkgkxvr7+5NCr0VqjRX4GYlE1Eql8r4d9KWr9wcloj0vY286by0N9vX1vWl6A6dqsOpkFSTTw11dXTG58M63zYHaKQzPP37eUp3c2tq6MDY29hfmltdqnRGqw+F4Vi7QOZ4WlIhkKB8EeUdGRoICS7kncFtb2+tyYWWDs1aIpKK7lqyiadpkQ2ARf2JdVdUB+fOXO6xlurZTnUPnaG9vr+Mu4OXlZWV4eFjr7u52YNN5+fPnP1nL9Hu6Bvh8qVTSCENiKjYD2sAueP+3FOj4sLVQS8WZ9ywHqU7P+v3+3Pj4eGl1dbVios/OziqoNaWzs1ODZQm5e6CLtUzUVCShPP/AoMbjcRWg5poJjA+lUChomUxGQ8f6VQpMX2At06gNGLpvsWpyKcz2wQ4ODszF/f19q4CmH1NYK0RS7z5TDXMsFltj1WO1gPnU1BTr6emhA+VLS0trCE2Gfk4gv0Pj7NQUuqzUHNP6+jo5owDDArfqGJlnAkej0X9g4Vdy/Qosf9LHmiYK8dJE9XtnZ+fzlZWVREdHh0HfcNLEMYEnJycNAWwg+yoLCwtX8/n8bfpHDf/6awoLjze4yhp4Snu94pKgsx0aGvoMo3F0dGTgOI16GTKAtp/BVUh1/Hg4HH4FiXbLfsnGU5y/8bXBA18Y3PPBMQ9/YvC3vzH4D/HaC5lkQ6HQNDrhsMvl6odOL8rJSZeQHZicoTruBJ9rb29/FOOl+fn5V7PZ7G1+SiIZkkXfvwQ9j4B9ON8OgXFX4DS0NTdq+SzmA7D0IsYxcGB7e/tL6DPuB4gekKG9gUDgBYA+DdmLIoLdYBdhSGClLtw6uB3shoDHMAw39FE3cwSDwYdmZmaeQud50ePxnEP4ekkIIb2TTCZje3t7Py0uLl7f3NxMAxQ2lHL4nQX/K8YCuMTE1VgtNlwUc3Nz1Fl0r9frKhaLLoTMTUZAERmjQ5nOqjcayXJd15VyuUxJw7GvjLGMfQSSdbvdWSICRXc0W6X9bOvPmsLhEMnmFCFyQmmbBCcwKQtQGgi4QsAClN4gOTwo8um0+R4hTyvM9hDQ2L3J9AJhNaDMIAKggeZSxrQCNkehlDiP7zyOIIfkzEEmjzIqoG5L6NGGHbSRx5JUVj1zh2DTY5y9jhrXoFyFXtNArBlYq8DIIi79IhKzdHh4SMaUpQPNAtuvS4qKhnKgm0vHm0yzGcbRkTiaAxehLKNWyUOaUxUY9a/LZsl8Dglw8tiJ65PO3CPZ5/N5qAzZcT44RJTU+ldlS0RKhCIz/Dg3XY7IVjMiYrSSrhmPWqFGcqcK6X9czfgLQYqNowAAAABJRU5ErkJggg==',
      iconSize: [26, 26],
      iconAnchor: [13, 13],
      popupAnchor: [0, -7],
    }),
    magenta: L.icon({
      iconUrl:
        'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMy43NzgzIDYuMjI0MTJDMTkuNTAwMyAxLjk0NjEzIDEyLjQ5OTkgMS45NDYxMyA4LjIyMTkzIDYuMjI0MTJDMy45NDM5MyAxMC41MDIxIDMuOTQzOTMgMTcuNTAyNSA4LjIyMTkzIDIxLjc4MDVMMTYuMDAwMSAyOS41NTg2TDIzLjc3ODMgMjEuNzgwNUMyOC4wNTYzIDE3LjUwMjUgMjguMDU2MyAxMC41MDIxIDIzLjc3ODMgNi4yMjQxMlpNMTYuMDAwMSAxOC4wMDIzQzE4LjIwOTIgMTguMDAyMyAyMC4wMDAxIDE2LjIxMTQgMjAuMDAwMSAxNC4wMDIzQzIwLjAwMDEgMTEuNzkzMiAxOC4yMDkyIDEwLjAwMjMgMTYuMDAwMSAxMC4wMDIzQzEzLjc5MSAxMC4wMDIzIDEyLjAwMDEgMTEuNzkzMiAxMi4wMDAxIDE0LjAwMjNDMTIuMDAwMSAxNi4yMTE0IDEzLjc5MSAxOC4wMDIzIDE2LjAwMDEgMTguMDAyM1oiIGZpbGw9IiNDOTM2NzUiLz4KPC9zdmc+Cg==',
      iconSize: [32, 32],
      iconAnchor: [16, 16],
      popupAnchor: [0, -8],
    }),
  })
  static markerIcons = MapController.createMarkerIcons()

  initialize() {
    this.kaartId = 'taken_kaart'
    this.preventScroll = false
    this.element[this.identifier] = this
    this.markerList = []
    this.markerMe = null
    this.markers = null
    this.buurten = null
    this.kaartModus = this.getKaartModus()
    // Reset de kaart naar de gecachete positie
    const cachedPosition = this.getCachedPosition()
    const initialCenter =
      this.kaartModus === KaartModus.VOLGEN && cachedPosition
        ? cachedPosition
        : [StandaardKaartCenter.coords.latitude, StandaardKaartCenter.coords.longitude]
    const initialZoom =
      this.kaartModus === KaartModus.VOLGEN && cachedPosition ? this.getZoom() : StandaardKaartZoom
    this.map = L.map(this.kaartId, {
      zoom: initialZoom,
      center: initialCenter,
    })
    this.map.on('zoomend', () => {
      if (this.kaartModus === KaartModus.VOLGEN) {
        this.setZoom(this.map.getZoom())
      }
    })
    this.map.on('dragstart', () => {
      this.kaartModus = null
      this.setKaartModusStorage(null)
      if (this.hasTakenOverzichtOutlet) {
        this.takenOverzichtOutlet.setKaartModus(this.kaartModus)
      }
    })

    this.drawMap()
    this.createMarkersLayer()

    this.mapLayers = {
      buurten: {
        layer: L.tileLayer.wms(
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
        ),
        legend: [],
      },
      EGD: {
        layer: L.tileLayer.wms(
          'https://www.gis.rotterdam.nl/GisWeb2/js/modules/kaart/WmsHandler.ashx',
          {
            layers: 'BSB.OBJ.EGD',
            format: 'image/png',
            transparent: true,
            minZoom: 10,
            maxZoom: 19,
          }
        ),
      },
    }
  }
  connect() {}
  getZoom() {
    return sessionStorage.getItem('kaartZoom') || StandaardKaartZoom
  }
  setZoom(zoom) {
    sessionStorage.setItem('kaartZoom', zoom)
  }
  getKaartModus() {
    return sessionStorage.getItem('kaartModus') || KaartModus.TOON_ALLES
  }
  setKaartModusStorage(kaartModus) {
    if (kaartModus) {
      sessionStorage.setItem('kaartModus', kaartModus)
    } else {
      sessionStorage.removeItem('kaartModus')
    }
  }
  getCachedPosition() {
    const cached = sessionStorage.getItem('lastPosition')
    if (!cached) return null
    const [lat, lng] = cached.split(',').map(Number)
    return [lat, lng]
  }
  setCachedPosition(lat, lng) {
    sessionStorage.setItem('lastPosition', `${lat},${lng}`)
  }
  drawMap = () => {
    const url =
      'https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{layerName}/{crs}/{z}/{x}/{y}.{format}'

    const config = {
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

    L.tileLayer(url, config).addTo(this.map)

    this.setupResizeObserver()
  }

  setupResizeObserver = () => {
    const resizeObserver = new ResizeObserver(() => {
      this.map.invalidateSize()
      // We gebruiken deze keepPopupOpen boolean omdat de kaart lijkt te resizen bij initieel laden.
      if (!this.keepPopupOpen) {
        this.map.closePopup()
      }
    })
    resizeObserver.observe(document.getElementById(this.kaartId))
  }
  createMarkersLayer = () => {
    this.markers = new L.featureGroup()
    this.map.addLayer(this.markers)
  }
  selectTaakMarker(taakUuid, preventScroll) {
    const obj = this.markerList.find((obj) => obj.options.taakUuid == taakUuid)
    this.preventScroll = preventScroll
    if (obj) {
      this.keepPopupOpen = true
      obj.openPopup()
      // We gebruiken deze keepPopupOpen boolean omdat de kaart lijkt te resizen bij initieel laden.
      setTimeout(() => {
        this.keepPopupOpen = false
      }, 500)
    }
  }
  toonAlles = () => this.map.fitBounds(this.markers.getBounds())
  volgen = () => this.map.setView(this.markerMe.getLatLng(), this.getZoom())

  kaartModusChangeHandler = (kaartModus) => {
    this.kaartModus = kaartModus
    this.setKaartModusStorage(kaartModus)
    if (!Object.keys(this.markers.getBounds()).length) {
      return
    }
    if (!this.markerMe) {
      this.toonAlles()
      return
    }
    switch (this.kaartModus) {
      case KaartModus.VOLGEN:
        this.volgen()
        break

      case KaartModus.TOON_ALLES:
        this.setZoom(this.map.getZoom())
        this.toonAlles()
        break
    }
  }

  kaartLayerChangeHandler(event) {
    console.log(event)
    if (event.target.checked) {
      this.mapLayers[event.params.mapLayerType].layer.addTo(this.map)
    } else {
      this.map.removeLayer(this.mapLayers[event.params.mapLayerType].layer)
    }
  }

  onTwoFingerDrag(event) {
    if (event.type === 'touchstart' && event.touches.length === 1) {
      event.currentTarget.classList.add('swiping')
    } else {
      event.currentTarget.classList.remove('swiping')
    }
  }
  positionChangeEvent = (position) => {
    const lat = position.coords.latitude
    const lng = position.coords.longitude
    this.setCachedPosition(lat, lng)
    if (!this.markerMe) {
      this.markerMe = new L.Marker([lat, lng], {
        icon: MapController.markerIcons.blue,
      })
      this.markers.addLayer(this.markerMe)
    } else {
      this.markerMe.setLatLng([lat, lng])
    }
    if (this.kaartModus === KaartModus.VOLGEN) {
      this.volgen()
    }
  }

  // grote wens voor EGD-laag op kaart in taakoverzicht
  // daarom buurten uitgezet, komt later weer terug als kaart gerefactored wordt.
  // toggleBuurten = () => {
  //   const checkbox = this.element.querySelector('#buurten-checkbox')
  //   const button = this.element.querySelector('#buurten-button')
  //   const isChecked = (checkbox.checked = !checkbox.checked)

  //   if (isChecked) {
  //     this.mapLayers['buurten'].layer.addTo(this.map)
  //   } else {
  //     this.map.removeLayer(this.mapLayers['buurten'].layer)
  //   }

  //   button.classList.toggle('active', isChecked)
  //   checkbox.classList.toggle('active', isChecked)
  // }

  makeRoute = (e) => {
    e.preventDefault()
    const event = new CustomEvent('openModalFromMap', {
      bubbles: true,
      cancelable: false,
      detail: { e },
    })
    this.map.closePopup()
    this.element.dispatchEvent(event)
  }
  taakPopupTargetConnected(taakPopup) {
    if (this.hasTakenLijstOutlet) {
      this.takenLijstOutlet.selecteerTaakItem(taakPopup.dataset.taakUuid, this.preventScroll)
    }
  }
  taakPopupTargetDisconnected(taakPopup) {
    if (this.hasTakenLijstOutlet) {
      this.takenLijstOutlet.deselecteerTaakItem(taakPopup.dataset.taakUuid)
    }
  }
  clearTaakMarker(taakUuid) {
    const marker = this.markerList.find((obj) => obj.options.taakUuid === taakUuid)
    this.markerList = this.markerList.filter((obj) => obj.options.taakUuid != taakUuid)
    this.markers.removeLayer(marker)
  }
  plotTaakMarker(markerData) {
    const lat = markerData.geometrie.coordinates ? markerData.geometrie.coordinates[1] : 51.9247772
    const long = markerData.geometrie.coordinates ? markerData.geometrie.coordinates[0] : 4.4780972
    const adres = markerData.adres
    const afbeelding = markerData.afbeeldingUrl
    const titel = markerData.titel
    const taakUuid = markerData.taakUuid

    const markerLocation = new L.LatLng(lat, long)

    const marker = new L.Marker(markerLocation, {
      icon: MapController.markerIcons.magenta,
      taakUuid: taakUuid,
    }).on('click', () => {
      this.preventScroll = false
    })

    const paragraphDistance = `<p>Afstand: <span data-taken-overzicht-target="taakAfstand" data-latitude="${lat}" data-longitude="${long}"></span></p>`
    const spanRemark = markerData.hasRemark
      ? `<span class="badge-count badge-count--info">i</span>`
      : ''
    const anchorDetail = `<a href="/taak/${taakUuid}" target="_top" aria-label="Bekijk taak ${taakUuid}">Details ${spanRemark}</a>`
    const anchorNavigeer = `<a href="#" data-action="modal#openModal" data-modal-action-param="/navigeer/${lat}/${long}">Navigeren</a>`
    const divDetailNavigeer = `<div class="">${anchorDetail} ${anchorNavigeer}</div>`

    const popupContent = afbeelding
      ? `<div data-taken-kaart-target="taakPopup" data-taak-uuid="${taakUuid}" class="container__image"><img src=${afbeelding}></div><div class="container__content"><h5 class="no-margin">${adres}</h5><p>${titel}</p>${paragraphDistance}${divDetailNavigeer}</div>`
      : `<div data-taken-kaart-target="taakPopup" data-taak-uuid="${taakUuid}" ></div><div class="container__content"><h5 class="no-margin">${adres}</h5><p>${titel}</p>${paragraphDistance}${divDetailNavigeer}</div>`

    marker.bindPopup(popupContent, { maxWidth: 460 })

    this.markers.addLayer(marker)
    this.markerList.push(marker)
    return marker
  }
  takenLijstOutletConnected(takenLijst) {
    const alleTakenKaartMarkersData = takenLijst.getKaartMarkers()
    const huidigeTaakUuids = this.markerList.map((obj) => obj.options.taakUuid)
    huidigeTaakUuids
      .filter(
        (taakUuid) =>
          !alleTakenKaartMarkersData.map((markerData) => markerData.taakUuid).includes(taakUuid)
      )
      .map((taakUuid) => {
        this.clearTaakMarker(taakUuid)
      })
    alleTakenKaartMarkersData
      .filter((markerData) => !huidigeTaakUuids.includes(markerData.taakUuid))
      .map((markerData) => {
        this.plotTaakMarker(markerData)
      })
    const selectedInput = this.element
      .closest('form')
      ?.querySelector('input[name="selected_taak_uuid"]')
    if (selectedInput && selectedInput.value) {
      this.selectTaakMarker(selectedInput.value, false)
    }
  }
}
