import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

function addMqListener(mq, handler) {
  if (mq.addEventListener) mq.addEventListener('change', handler)
  else mq.addListener(handler) // legacy Safari
}

function removeMqListener(mq, handler) {
  if (mq.removeEventListener) mq.removeEventListener('change', handler)
  else mq.removeListener(handler)
}
export default class extends Controller {
  static outlets = ['kaart']
  static values = {
    taakCoordinates: String,
    areaList: String,
    currentDistrict: String,
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
    'dotList',
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
    'sectionimageslider',
    'imageslidermobile',
    'imagesliderdesktop',
  ]

  Mapping = {
    fotos: 'media',
  }

  initialize() {
    this.markerIcons = {
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
    }
    this.markers = null
    this.markerMe = null
    this.map = null
    this.currentPosition = null
    this.fullSizeImageContainer = null
    this.selectedImageIndex = null
    this.sliderContainerWidth = 0
    this.isZooming = false
    this.taakCoordinates = JSON.parse(this.taakCoordinatesValue)

    this.initMessages()

    this.imagesList = JSON.parse(this.afbeeldingenValue).map(
      (bestand) => bestand.afbeelding_relative_url
    )

    if (this.hasThumbListTarget) {
      this.thumbListTarget.getElementsByTagName('li')[0].classList.add('selected')
      this.sliderContainerWidth = this.thumbListTarget.parentElement.clientWidth

      screen.orientation.addEventListener('change', () => {
        this.sliderContainerWidth = this.thumbListTarget.parentElement.clientWidth
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
        if (e.touches.length === 1 && !this.isZooming) {
          startX = e.touches[0].clientX
        }
      })
      this.selectedImageModalTarget.addEventListener('touchend', (e) => {
        if (e.changedTouches.length === 1 && !this.isZooming) {
          let endX = e.changedTouches[0].clientX
          if (startX - endX > 50) this.showNextImageInModal()
          if (endX - startX > 50) this.showPreviousImageInModal()
        }
      })
    }
    // END SWIPE
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
    this.markers = new L.featureGroup()
    if (this.taakCoordinates.length && !this.map) {
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
      this.map = L.map('taken_kaart', {
        dragging: !L.Browser.mobile,
        tap: !L.Browser.mobile,
        twoFingerZoom: true,
      }).setView(this.taakCoordinates, 18)
      L.tileLayer(url, config).addTo(this.map)
      const marker = L.marker(this.taakCoordinates, { icon: this.markerIcons.magenta }).addTo(
        this.map
      )
      this.markers.addLayer(marker)
    }
    // document.querySelectorAll('.container__image').forEach((element) => {
    //   this.pinchZoom(element)
    // })
  }

  connect() {
    this.scrollTimeout = null
    this.activeIndexValue = 0
    this.preloadImagesAround(this.activeIndexValue)
    this.mq = window.matchMedia('(min-width: 1024px)')
    this._onMqChange = (e) => this.placeSlider(e.matches)
    this.currentScrollIndex = null

    addMqListener(this.mq, this._onMqChange)

    // Initieel meteen goed zetten
    this.placeSlider(this.mq.matches)

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

    this.showHideImageNavigation()
  }

  imageSliderThumbContainerConnected() {
    if (this.getBrowser().includes('safari') && !navigator.userAgent.includes('Chrome')) {
      document.body.classList.add('css--safari')
      setTimeout(() => {
        this.imageSliderThumbContainerTarget.querySelector('.container__image img').click()
      }, 600)
    }
  }

  disconnect() {
    if (this.mq && this._onMqChange) {
      removeMqListener(this.mq, this._onMqChange)
    }
    window.removeEventListener(
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
  }

  placeSlider(isDesktop) {
    if (!this.hasSectionimagesliderTarget) return
    if (!this.hasImageslidermobileTarget || !this.hasImagesliderdesktopTarget) return
    const host = isDesktop ? this.imagesliderdesktopTarget : this.imageslidermobileTarget
    if (this.sectionimagesliderTarget.parentNode !== host) {
      host.appendChild(this.sectionimagesliderTarget)
    }
  }

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
      this.mapLayers[e.params.mapLayerType].layer.addTo(this.map)
      this.map.setMinZoom(12)
    } else {
      this.map.removeLayer(this.mapLayers[e.params.mapLayerType].layer)
      this.map.setMinZoom(12)
    }
  }

  toggleDetailLocatie(element) {
    if (element.target.open) {
      this.map._onResize()
    }
  }

  taakAfstandTargetConnected(element) {
    let textContent = 'Afstand onbekend'
    if (this.currentPosition) {
      const markerLocation = new L.LatLng(this.taakCoordinates[0], this.taakCoordinates[1])
      textContent = `${this.formatDistance(
        Math.round(markerLocation.distanceTo(this.currentPosition))
      )}`
    }
    element.textContent = textContent
  }
  positionChangeEvent(position) {
    this.currentPosition = [position.coords.latitude, position.coords.longitude]
    if (!this.markerMe) {
      this.markerMe = new L.Marker(this.currentPosition, {
        icon: this.markerIcons.blue,
      })
      this.markers.addLayer(this.markerMe)
    }
    this.markerMe.setLatLng(this.currentPosition)
    if (this.hasTaakAfstandTarget && this.taakCoordinates) {
      this.taakAfstandTargetConnected(this.taakAfstandTarget)
    }
    if (this.hasNavigeerLinkTarget) {
      const linkList = document.querySelectorAll('[data-taak-detail-target="navigeerLink"]')

      for (const link of linkList) {
        const href = link.getAttribute('href')
        const rx = new RegExp('saddr=[\\d\\D]*?&', 'g')
        const newHref = href.replace(rx, `saddr=${this.currentPosition}&`)
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
    if (this.hasMercurePublicUrlValue && this.isValidHttpUrl(this.mercurePublicUrlValue)) {
      const url = new URL(this.mercurePublicUrlValue)
      url.searchParams.append('topic', window.location.pathname)
      if (this.hasMercureSubscriberTokenValue) {
        url.searchParams.append('authorization', this.mercureSubscriberTokenValue)
      }
      this.eventSource = new EventSource(url)
      this.eventSource.onmessage = (e) => this.onMessage(e)
      this.eventSource.onerror = (e) => this.onMessageError(e)
    }
  }
  onMessage(e) {
    let data = JSON.parse(e.data)
    let turboFrame = document.getElementById('taak_basis')
    turboFrame.src = data.url
  }
  onMessageError() {
    this.eventSource.close()
  }

  mappingFunction(object) {
    const result = {}
    for (const key in this.Mapping) {
      const newKey = this.Mapping[key]
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
    const index = Math.floor(
      this.imageSliderContainerTarget.scrollLeft / this.imageSliderContainerTarget.offsetWidth
    )

    if (index !== this.currentScrollIndex) {
      this.currentScrollIndex = index
      this.highlightThumb(index)
    }

    clearTimeout(this.scrollTimeout)

    this.scrollTimeout = setTimeout(() => {
      this.updateActiveIndex()
    }, 80)
  }

  selectImage(e) {
    this.imageScrollInView(Number(e.params.imageIndex) - 1)
    this.highlightThumb(Number(e.params.imageIndex) - 1)
  }

  updateActiveIndex() {
    console.log('updateActiveIndex')
    const container = this.imageSliderContainerTarget
    if (!container || !this.imageTargets.length) return

    const itemWidth = container.clientWidth
    const index = Math.round(container.scrollLeft / itemWidth)

    if (index === this.activeIndexValue) return

    this.activeIndexValue = index
    // this.onActiveIndexChanged(index)
  }

  ensureThumbVisibleByIndex(index) {
    const container = this.imageSliderThumbContainerTarget
    const thumbList = this.thumbListTarget
    const thumbLi = thumbList.querySelectorAll('li')[index - 1] // let op: jouw thumb index-param is forloop.counter (1-based)

    if (!thumbLi) return

    // Als er geen overflow is: niets doen
    if (container.scrollWidth <= container.clientWidth) return

    const cRect = container.getBoundingClientRect()
    const tRect = thumbLi.getBoundingClientRect()
    const padding = 8

    const isLeftOutside = tRect.left < cRect.left + padding
    const isRightOutside = tRect.right > cRect.right - padding
    if (!isLeftOutside && !isRightOutside) return

    // Scroll naar center van de thumb
    const thumbCenterInContainer = tRect.left - cRect.left + container.scrollLeft + tRect.width / 2

    const targetLeft = thumbCenterInContainer - container.clientWidth / 2
    const maxScroll = container.scrollWidth - container.clientWidth
    const clamped = Math.max(0, Math.min(targetLeft, maxScroll))

    container.scrollTo({ left: clamped, behavior: 'smooth' })
  }

  highlightThumb(index) {
    console.log('highlightThumb', index)
    if (index === this.currentThumbIndex) return
    this.currentThumbIndex = index
    this.deselectThumbs(this.thumbListTarget)
    this.thumbListTarget.getElementsByTagName('li')[index].classList.add('selected')
    this.ensureThumbVisibleByIndex(index)
  }

  onActiveIndexChanged(index) {
    console.log('onActiveIndexChanged')
    this.updateDots(index)
    this.highlightThumb(index)
    this.preloadImagesAround(index)
  }

  preloadImagesAround(index) {
    const max = this.imageTargets.length - 1

    ;[index - 1, index, index + 1]
      .filter((i) => i >= 0 && i <= max)
      .forEach((i) => this.loadImageAtIndex(i))
  }

  loadImageAtIndex(index) {
    const li = this.imageTargets[index]
    if (!li) return

    const img = li.querySelector('img')
    if (!img || img.src) return

    if (img.dataset.src) {
      img.src = img.dataset.src
    }
  }

  deselectThumbs(list) {
    for (const item of list.querySelectorAll('li')) {
      item.classList.remove('selected')
    }
  }

  updateDots(index) {
    for (const item of this.dotListTarget.querySelectorAll('.dot')) {
      item.classList.remove('selected')
    }
    this.dotListTarget.getElementsByClassName('dot')[index].classList.add('selected')
  }

  imageScrollInView(index) {
    const img = this.imageSliderContainerTarget.querySelector(`ul :nth-child(${index + 1}) img`)
    !img.src && img.setAttribute('src', img.dataset.src)
    this.imageSliderContainerTarget.scrollTo({
      left: Number(index) * this.imageSliderContainerTarget.offsetWidth,
      top: 0,
    })
  }

  showPreviousImageInModal() {
    if (!this.isZooming) {
      this.selectedImageIndex =
        (this.selectedImageIndex - 1 + this.imagesList.length) % this.imagesList.length
      this.showImage(true)
    }
  }

  showNextImageInModal() {
    if (!this.isZooming) {
      this.selectedImageIndex = (this.selectedImageIndex + 1) % this.imagesList.length
      this.showImage(true)
    }
  }

  showImage(inModal = false) {
    console.log('showImage')
    const img = this.selectedImageModalTarget.querySelector('img')
    const sd = this.signedDataValue ? `?signed-data=${this.signedDataValue}` : ''
    img.src = `${this.urlPrefixValue}${this.imagesList[this.selectedImageIndex]}${sd}`
    this.isZooming = false
    this.showHideImageNavigation()
    this.imageCounterTarget.textContent = `Foto ${this.selectedImageIndex + 1} van ${
      this.imagesList.length
    }`
    const selectedImageData = JSON.parse(
      this.imageTargets[this.selectedImageIndex].dataset.imageData
    )

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
    this.imageScrollInView(this.selectedImageIndex) //image in detailpage
    this.highlightThumb(this.selectedImageIndex)
    this.fullSizeImageContainer = this.selectedImageModalTarget
  }

  showNormal() {
    this.fullSizeImageContainer.classList.remove('fullSize')
    this.fullSizeImageContainer.style.backgroundPosition = '50% 50%'
    window.removeEventListener('mousemove', this.getRelativeCoordinates, true)
    this.isZooming = false
  }

  showHideImageNavigation() {
    if (this.imagesList.length > 1) {
      this.navigateImagesLeftTargets.forEach((button) => {
        button.classList.remove('inactive')
      })
      this.navigateImagesRightTargets.forEach((button) => {
        button.classList.remove('inactive')
      })
      if (this.selectedImageIndex === 0 || !this.selectedImageIndex) {
        this.navigateImagesLeftTargets.forEach((button) => {
          button.classList.add('inactive')
        })
      }
      if (this.selectedImageIndex === this.imagesList.length - 1) {
        this.navigateImagesRightTargets.forEach((button) => {
          button.classList.add('inactive')
        })
      }
    }
  }

  showImageInModal(e) {
    this.selectedImageIndex = e.params.imageIndex
    const modal = this.modalImagesTarget
    const modalBackdrop = document.querySelector('.modal-backdrop')
    modal.classList.add('show')
    modalBackdrop.classList.add('show')
    document.body.classList.add('show-modal')
    this.isZooming = false
    this.showImage(true)
  }

  getBrowser() {
    let userAgent = navigator.userAgent
    let browser = 'onbekend'
    if (/Safari/.test(userAgent)) {
      browser = 'safari'
    }
    return browser
  }

  closeModal() {
    const modalList = this.element.querySelectorAll('.modal')
    const modalBackdrop = this.element.querySelector('.modal-backdrop')
    if (this.hasTurboFrameTarget) {
      this.turboFrameTarget.innerHTML = ''
    }

    modalList.forEach((modal) => {
      modal.classList.remove('show')
    })
    modalBackdrop.classList.remove('show')
    document.body.classList.remove('show-modal', 'show-modal--transparent', 'show-navigation')
  }

  formatDistance(meters) {
    if (meters < 50) {
      return `${Math.round(meters)} m`
    }
    if (meters < 96) {
      return `${Math.round(meters / 5) * 5} m`
    }
    const km = meters / 1000
    if (km < 99.9) {
      return `${(Math.round(km * 10) / 10).toLocaleString('nl-NL', {
        minimumFractionDigits: 1,
      })} km`
    }
    return `${Math.round(km).toLocaleString('nl-NL')} km`
  }

  foldout(e) {
    console.log(e.target)
    e.target.parentElement.classList.toggle('show')
  }
}
