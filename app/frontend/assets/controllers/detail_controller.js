import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

let markerIcon,
  markerBlue,
  markerMagenta,
  markerMe,
  markers,
  map,
  currentPosition,
  imagesList,
  fullSizeImageContainer = null

let selectedImageIndex,
  sliderContainerWidth = 0
let isZooming = false

let self = null
export default class extends Controller {
  static outlets = ['kaart']
  static values = {
    incidentX: String,
    incidentY: String,
    areaList: String,
    currentDistrict: String,
    incidentObject: Object,
    mercurePublicUrl: String,
    mercureSubscriberToken: String,
    afbeeldingen: String,
    urlPrefix: String,
    signedData: String,
  }
  static targets = [
    'selectedImageModal',
    'selectedImageLabel',
    'selectedImageSubLabel',
    'thumbList',
    'image',
    'imageSliderContainer',
    'taakAfstand',
    'navigeerLink',
    'modalImages',
    'navigateImagesLeft',
    'navigateImagesRight',
    'navigateImagesRight',
    'imageCounter',
    'imageSliderThumbContainer',
    'btnToTop',
  ]

  Mapping = {
    fotos: 'media',
  }

  initialize() {
    self = this
    let childControllerConnectedEvent = new CustomEvent('childControllerConnectedEvent', {
      bubbles: true,
      cancelable: false,
      detail: {
        controller: self,
      },
    })

    window.dispatchEvent(childControllerConnectedEvent)
    self.initMessages()

    imagesList = JSON.parse(this.afbeeldingenValue).map(
      (bestand) => bestand.afbeelding_relative_url
    )

    if (self.hasThumbListTarget) {
      self.thumbListTarget.getElementsByTagName('li')[0].classList.add('selected')
      sliderContainerWidth = self.thumbListTarget.parentElement.clientWidth

      screen.orientation.addEventListener('change', () => {
        sliderContainerWidth = self.thumbListTarget.parentElement.clientWidth
      })
    }

    document.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowLeft') {
        this.showPreviousImageInModal()
      }
      if (event.key === 'ArrowRight') {
        this.showNextImageInModal()
      }
    })

    //START SWIPE

    let startX = 0

    if (this.hasSelectedImageModalTarget) {
      this.selectedImageModalTarget.addEventListener('touchstart', (e) => {
        e.preventDefault()
        console.log('touchStart')
        if (e.touches.length === 1 && !isZooming) {
          startX = e.touches[0].clientX
        }
      })
      this.selectedImageModalTarget.addEventListener('touchend', (e) => {
        if (e.changedTouches.length === 1 && !isZooming) {
          let endX = e.changedTouches[0].clientX
          if (startX - endX > 50) this.showNextImageInModal()
          if (endX - startX > 50) this.showPreviousImageInModal()
        }
      })
    }
    // END SWIPE

    const mapDiv = document.getElementById('incidentMap')
    this.mapLayers = {
      containers: {
        layer: L.tileLayer.wms(
          'https://www.gis.rotterdam.nl/GisWeb2/js/modules/kaart/WmsHandler.ashx',
          {
            layers: 'OBS.OO.CONTAINER',
            format: 'image/png',
            transparent: true,
            minZoom: 10,
            maxZoom: 19,
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

    if (mapDiv) {
      markers = new L.featureGroup()
      markerIcon = L.Icon.extend({
        options: {
          iconSize: [26, 26],
          iconAnchor: [13, 13],
          popupAnchor: [0, -17],
        },
      })

      markerBlue = new markerIcon({
        iconUrl:
          'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAATESURBVHgBrVZNTGNVFL7vp9AfCB0mpAOSoRgdGUQcI8yiCYImGjXExBBYGbshcdGiKxHHhSVRdG+M0YWrccUC4qSz0EQT2RATiNHEBFKcjnYmg6BtLfa/7/qdx72vr50OU+qc5OTed9895zvn3HPOvYw1SZxzL/gt8Br4Bq8Szb8HB8F+9qAolUqdgcIIOMmbowj7vwQlg3XeNUu/5XK5wZN0Kw3AFBCDoN/pdH6HJb/8t3GTsWu7nEV3GbuZOl4b9TH2BPjKhMIGvDWqboCfA8dJ34nAApRjqmK+J0FTecY+2uDs0x/ZiRS6fGxAl7MKnkgkxvr7+5NCr0VqjRX4GYlE1Eql8r4d9KWr9wcloj0vY286by0N9vX1vWl6A6dqsOpkFSTTw11dXTG58M63zYHaKQzPP37eUp3c2tq6MDY29hfmltdqnRGqw+F4Vi7QOZ4WlIhkKB8EeUdGRoICS7kncFtb2+tyYWWDs1aIpKK7lqyiadpkQ2ARf2JdVdUB+fOXO6xlurZTnUPnaG9vr+Mu4OXlZWV4eFjr7u52YNN5+fPnP1nL9Hu6Bvh8qVTSCENiKjYD2sAueP+3FOj4sLVQS8WZ9ywHqU7P+v3+3Pj4eGl1dbVios/OziqoNaWzs1ODZQm5e6CLtUzUVCShPP/AoMbjcRWg5poJjA+lUChomUxGQ8f6VQpMX2At06gNGLpvsWpyKcz2wQ4ODszF/f19q4CmH1NYK0RS7z5TDXMsFltj1WO1gPnU1BTr6emhA+VLS0trCE2Gfk4gv0Pj7NQUuqzUHNP6+jo5owDDArfqGJlnAkej0X9g4Vdy/Qosf9LHmiYK8dJE9XtnZ+fzlZWVREdHh0HfcNLEMYEnJycNAWwg+yoLCwtX8/n8bfpHDf/6awoLjze4yhp4Snu94pKgsx0aGvoMo3F0dGTgOI16GTKAtp/BVUh1/Hg4HH4FiXbLfsnGU5y/8bXBA18Y3PPBMQ9/YvC3vzH4D/HaC5lkQ6HQNDrhsMvl6odOL8rJSZeQHZicoTruBJ9rb29/FOOl+fn5V7PZ7G1+SiIZkkXfvwQ9j4B9ON8OgXFX4DS0NTdq+SzmA7D0IsYxcGB7e/tL6DPuB4gekKG9gUDgBYA+DdmLIoLdYBdhSGClLtw6uB3shoDHMAw39FE3cwSDwYdmZmaeQud50ePxnEP4ekkIIb2TTCZje3t7Py0uLl7f3NxMAxQ2lHL4nQX/K8YCuMTE1VgtNlwUc3Nz1Fl0r9frKhaLLoTMTUZAERmjQ5nOqjcayXJd15VyuUxJw7GvjLGMfQSSdbvdWSICRXc0W6X9bOvPmsLhEMnmFCFyQmmbBCcwKQtQGgi4QsAClN4gOTwo8um0+R4hTyvM9hDQ2L3J9AJhNaDMIAKggeZSxrQCNkehlDiP7zyOIIfkzEEmjzIqoG5L6NGGHbSRx5JUVj1zh2DTY5y9jhrXoFyFXtNArBlYq8DIIi79IhKzdHh4SMaUpQPNAtuvS4qKhnKgm0vHm0yzGcbRkTiaAxehLKNWyUOaUxUY9a/LZsl8Dglw8tiJ65PO3CPZ5/N5qAzZcT44RJTU+ldlS0RKhCIz/Dg3XY7IVjMiYrSSrhmPWqFGcqcK6X9czfgLQYqNowAAAABJRU5ErkJggg==',
      })
      markerMagenta = new markerIcon({
        iconUrl:
          'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMy43NzgzIDYuMjI0MTJDMTkuNTAwMyAxLjk0NjEzIDEyLjQ5OTkgMS45NDYxMyA4LjIyMTkzIDYuMjI0MTJDMy45NDM5MyAxMC41MDIxIDMuOTQzOTMgMTcuNTAyNSA4LjIyMTkzIDIxLjc4MDVMMTYuMDAwMSAyOS41NTg2TDIzLjc3ODMgMjEuNzgwNUMyOC4wNTYzIDE3LjUwMjUgMjguMDU2MyAxMC41MDIxIDIzLjc3ODMgNi4yMjQxMlpNMTYuMDAwMSAxOC4wMDIzQzE4LjIwOTIgMTguMDAyMyAyMC4wMDAxIDE2LjIxMTQgMjAuMDAwMSAxNC4wMDIzQzIwLjAwMDEgMTEuNzkzMiAxOC4yMDkyIDEwLjAwMjMgMTYuMDAwMSAxMC4wMDIzQzEzLjc5MSAxMC4wMDIzIDEyLjAwMDEgMTEuNzkzMiAxMi4wMDAxIDE0LjAwMjNDMTIuMDAwMSAxNi4yMTE0IDEzLjc5MSAxOC4wMDIzIDE2LjAwMDEgMTguMDAyM1oiIGZpbGw9IiNDOTM2NzUiLz4KPC9zdmc+Cg==',
      })

      let url =
        'https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{layerName}/{crs}/{z}/{x}/{y}.{format}'
      let config = {
        crs: 'EPSG:3857',
        format: 'png',
        name: 'standaard',
        layerName: 'standaard',
        type: 'wmts',
        minZoom: 12,
        maxZoom: 19,
        tileSize: 256,
        attribution: '',
      }
      const incidentCoordinates = [
        parseFloat(self.incidentXValue.replace(/,/g, '.')),
        parseFloat(self.incidentYValue.replace(/,/g, '.')),
      ]
      map = L.map('incidentMap', {
        dragging: !L.Browser.mobile,
        tap: !L.Browser.mobile,
        twoFingerZoom: true,
      }).setView(incidentCoordinates, 18)
      L.tileLayer(url, config).addTo(map)
      const marker = L.marker(incidentCoordinates, { icon: markerMagenta }).addTo(map)

      markers.addLayer(marker)

      if (currentPosition) {
        markerMe = new L.Marker([currentPosition[0], currentPosition[1]], { icon: markerBlue })
        markers.addLayer(markerMe)
        markerMe.setLatLng([currentPosition[0], currentPosition[1]])
        L.marker(currentPosition, { icon: markerBlue }).addTo(map)
      }

      window.addEventListener('positionChangeEvent', function (e) {
        self.positionWatchSuccess(e.detail.position)
      })
    }

    document.querySelectorAll('.container__image').forEach((element) => {
      self.pinchZoom(element)
    })
  }

  connect() {
    window.addEventListener(
      'scroll',
      function () {
        if (this.hasBtnToTopTarget) {
          if (document.body.scrollTop >= 100 || document.documentElement.scrollTop >= 100) {
            this.btnToTopTarget.classList.add('show')
          } else {
            this.btnToTopTarget.classList.remove('show')
          }
        }
      }.bind(this),
      false
    )
    setTimeout(() => {
      this.scrollToTop()
    }, 100)

    if (this.getBrowser().includes('safari') && !navigator.userAgent.includes('Chrome')) {
      document.body.classList.add('css--safari')
      setTimeout(() => {
        this.imageSliderThumbContainerTarget.querySelector('.container__image img').click()
      }, 600)
    }
  }

  disconnect() {}

  scrollToTop(e) {
    if (e) {
      e.target.blur()
    }
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }

  onMapLayerChange(e) {
    if (e.target.checked) {
      this.mapLayers[e.params.mapLayerType].layer.addTo(map)
    } else {
      map.removeLayer(this.mapLayers[e.params.mapLayerType].layer)
    }
  }

  toggleDetailLocatie(element) {
    if (element.target.open) {
      map._onResize()
    }
  }

  taakAfstandTargetConnected(element) {
    const markerLocation = new L.LatLng(element.dataset.latitude, element.dataset.longitude)
    element.textContent = Math.round(markerLocation.distanceTo(currentPosition))
  }

  positionChangeEvent(position) {
    console.log('DETAIL, positionChangeEvent lat', position.coords.latitude)
    console.log('DETAIL, positionChangeEvent long', position.coords.longitude)
  }

  positionWatchSuccess(position) {
    let self = this
    console.log('detail.positionWatchSuccess')
    currentPosition = [position.coords.latitude, position.coords.longitude]
    if (self.hasTaakAfstandTarget) {
      const elem = self.taakAfstandTarget
      const markerLocation = new L.LatLng(elem.dataset.latitude, elem.dataset.longitude)
      const afstand = Math.round(markerLocation.distanceTo(currentPosition))
      elem.textContent = afstand
    }
    if (self.hasNavigeerLinkTarget) {
      const linkList = document.querySelectorAll('[data-detail-target="navigeerLink"]')

      for (const link of linkList) {
        const href = link.getAttribute('href')
        const rx = new RegExp('saddr=[\\d\\D]*?&', 'g')
        const newHref = href.replace(rx, `saddr=${currentPosition}&`)
        link.setAttribute('href', newHref)
      }
    }
  }

  makeRoute(event) {
    let routeUrl = 'https://www.google.com/maps/dir/?api=1&destination='
    if (event.params.map === 'waze') {
      routeUrl = 'https://www.waze.com/ul?ll='
    }

    function getRoute(event) {
      let lat = event.params.lat
      let long = event.params.long
      routeUrl += `${lat},${long}&navigate=yes`
      window.open(routeUrl, '_blank')
    }

    getRoute(event)
  }

  isValidHttpUrl(string) {
    let url

    try {
      url = new URL(string)
    } catch (_) {
      return false
    }

    return url.protocol === 'http:' || url.protocol === 'https:'
  }
  initMessages() {
    let self = this
    if (self.hasMercurePublicUrlValue && self.isValidHttpUrl(self.mercurePublicUrlValue)) {
      const url = new URL(self.mercurePublicUrlValue)
      url.searchParams.append('topic', window.location.pathname)
      if (self.hasMercureSubscriberTokenValue) {
        url.searchParams.append('authorization', self.mercureSubscriberTokenValue)
      }
      console.log(url)
      self.eventSource = new EventSource(url)
      self.eventSource.onmessage = (e) => self.onMessage(e)
      self.eventSource.onerror = (e) => self.onMessageError(e)
    }
  }
  onMessage(e) {
    let data = JSON.parse(e.data)
    console.log('mercure message', data)
    let turboFrame = document.getElementById('taak_basis')
    turboFrame.src = data.url
  }
  onMessageError(e) {
    let self = this
    console.log(e)
    console.log('An error occurred while attempting to connect.')
    self.eventSource.close()
  }

  mappingFunction(object) {
    let self = this
    const result = {}
    for (const key in self.Mapping) {
      const newKey = self.Mapping[key]
      if (Object.hasOwn(object, key)) {
        result[newKey] = object[key]
      } else {
        result[newKey] = null
      }
    }
    return result
  }

  onTwoFingerDrag(event) {
    if (event.type === 'touchstart' && event.touches.length === 1) {
      event.currentTarget.classList.add('swiping')
    } else {
      event.currentTarget.classList.remove('swiping')
    }
  }

  onScrollSlider() {
    let self = this
    self.highlightThumb(
      Math.floor(
        self.imageSliderContainerTarget.scrollLeft / self.imageSliderContainerTarget.offsetWidth
      )
    )
  }

  imageScrollInView(index) {
    this.imageSliderContainerTarget.scrollTo({
      left: Number(index) * this.imageSliderContainerTarget.offsetWidth,
      top: 0,
    })
  }

  selectImage(e) {
    let self = this
    self.imageSliderContainerTarget.scrollTo({
      left: (Number(e.params.imageIndex) - 1) * self.imageSliderContainerTarget.offsetWidth,
      top: 0,
    })
    self.deselectThumbs(e.target.closest('ul'))
    e.target.closest('li').classList.add('selected')
  }

  highlightThumb(index) {
    let self = this
    self.deselectThumbs(self.thumbListTarget)
    self.thumbListTarget.getElementsByTagName('li')[index].classList.add('selected')
    const thumb = this.thumbListTarget.getElementsByTagName('li')[index]
    const thumbWidth = thumb.offsetWidth
    const offsetNum = thumbWidth * index
    const maxScroll = this.thumbListTarget.offsetWidth - sliderContainerWidth

    const newLeft =
      offsetNum - sliderContainerWidth / 2 > 0
        ? offsetNum - sliderContainerWidth / 3 < maxScroll
          ? offsetNum - sliderContainerWidth / 3
          : maxScroll
        : 0

    this.thumbListTarget.style.left = `-${newLeft}px`
  }

  deselectThumbs(list) {
    for (const item of list.querySelectorAll('li')) {
      item.classList.remove('selected')
    }
  }

  showPreviousImageInModal() {
    if (!isZooming) {
      selectedImageIndex = (selectedImageIndex - 1 + imagesList.length) % imagesList.length
      console.log('showPreviousImageInModal', selectedImageIndex)
      this.showImage(true)
    }
  }

  showNextImageInModal() {
    if (!isZooming) {
      selectedImageIndex = (selectedImageIndex + 1) % imagesList.length
      console.log('showNextImageInModal', selectedImageIndex)
      this.showImage(true)
    }
  }

  showImage(inModal = false) {
    console.log('showImage,in modal?', inModal)
    const img = this.selectedImageModalTarget.querySelector('img')
    const sd = this.signedDataValue ? `?signed-data=${this.signedDataValue}` : ''
    img.src = `${this.urlPrefixValue}${imagesList[selectedImageIndex]}${sd}`
    isZooming = false
    this.showHideImageNavigation()
    this.imageCounterTarget.textContent = `Foto ${selectedImageIndex + 1} van ${imagesList.length}`
    const selectedImageData = JSON.parse(this.imageTargets[selectedImageIndex].dataset.imageData)
    // console.log('___selectedImageData', selectedImageData)

    if (selectedImageData.oorsprong != 'melder' || inModal) {
      if (selectedImageData.label) {
        this.selectedImageLabelTarget.textContent = selectedImageData.label
      }
      if (selectedImageData.bron_signaal_id && selectedImageData.bron_id) {
        this.selectedImageSubLabelTarget.textContent = `${selectedImageData.bron_id} - ${selectedImageData.bron_signaal_id}`
      } else {
        this.selectedImageSubLabelTarget.textContent = ''
      }
    }
    this.imageScrollInView(selectedImageIndex) //image in detailpage
    fullSizeImageContainer = this.selectedImageModalTarget
  }

  showNormal() {
    fullSizeImageContainer.classList.remove('fullSize')
    fullSizeImageContainer.style.backgroundPosition = '50% 50%'
    window.removeEventListener('mousemove', this.getRelativeCoordinates, true)
    isZooming = false
  }

  showHideImageNavigation() {
    this.navigateImagesLeftTarget.classList.remove('inactive')
    this.navigateImagesRightTarget.classList.remove('inactive')
    if (selectedImageIndex === 0) {
      this.navigateImagesLeftTarget.classList.add('inactive')
    }
    if (selectedImageIndex === imagesList.length - 1) {
      this.navigateImagesRightTarget.classList.add('inactive')
    }
  }

  showImageInModal(e) {
    selectedImageIndex = e.params.imageIndex
    const modal = this.modalImagesTarget
    const modalBackdrop = document.querySelector('.modal-backdrop')
    modal.classList.add('show')
    modalBackdrop.classList.add('show')
    document.body.classList.add('show-modal')
    isZooming = false
    this.showImage(true)
  }

  pinchZoom(imageElement) {
    console.log('pinchZoom')
    let imageElementScale = 1
    let start = {}
    // Calculate distance between two fingers
    const distance = (event) => {
      const dist = Math.hypot(
        event.touches[0].pageX - event.touches[1].pageX,
        event.touches[0].pageY - event.touches[1].pageY
      )
      return dist
    }

    imageElement.addEventListener('touchstart', (event) => {
      if (event.touches.length === 2) {
        event.preventDefault() // Prevent page scroll
        start.x = (event.touches[0].pageX + event.touches[1].pageX) / 2
        start.y = (event.touches[0].pageY + event.touches[1].pageY) / 2
        start.distance = distance(event)
      }
    })

    imageElement.addEventListener('touchmove', (event) => {
      if (event.touches.length === 2) {
        console.log('event.touches.length === 2')
        event.preventDefault() // Prevent page scroll
        isZooming = true
        let scale
        if (event.scale) {
          scale = event.scale
        } else {
          const deltaDistance = distance(event)
          scale = deltaDistance / start.distance
        }
        imageElementScale = Math.min(Math.max(1, scale), 4)

        const deltaX = ((event.touches[0].pageX + event.touches[1].pageX) / 2 - start.x) * 2
        const deltaY = ((event.touches[0].pageY + event.touches[1].pageY) / 2 - start.y) * 2
        const transform = `translate3d(${deltaX}px, ${deltaY}px, 0) scale(${imageElementScale})`
        imageElement.style.transform = transform
        imageElement.style.WebkitTransform = transform
        imageElement.style.zIndex = '9999'
      }
    })

    imageElement.addEventListener('touchend', () => {
      // Reset image to it's original format
      imageElement.style.transform = ''
      imageElement.style.WebkitTransform = ''
      imageElement.style.zIndex = ''
      setTimeout(() => (isZooming = false), 300)
    })
  }

  getBrowser() {
    let userAgent = navigator.userAgent
    let browser = 'onbekend'
    if (/Safari/.test(userAgent)) {
      browser = 'safari'
    }
    return browser
  }
}
