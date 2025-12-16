import { Controller } from '@hotwired/stimulus'

const SWIPE_TRESHOLD = 100
let scrollPositionForDialog = 0
export default class extends Controller {
  static targets = ['infosheet', 'scrollHandle', 'infosheetTurboframe']
  initialize() {
    this.sourceElemParent = null
  }

  connect() {
    console.log('infosheet connected')
  }
  scrollHandleTargetConnected(element) {
    this.startX = 0
    this.startY = 0
    this.currentX = 0
    this.currentY = 0
    this.isSwiping = false
    if ('ontouchstart' in window) {
      element.addEventListener('touchstart', (e) => {
        this.handleTouchStart(e)
      })

      element.addEventListener('touchmove', (e) => {
        this.handleTouchMove(e)
      })

      element.addEventListener('touchend', () => {
        this.handleTouchEnd()
      })
    }
  }

  handleTouchStart(e) {
    this.startX = e.touches[0].clientX
    this.startY = e.touches[0].clientY
    this.currentX = this.startX // in het geval gebruiker alleen mmar tapt ipv swipet
    this.currentY = this.startY
    this.isSwiping = true
  }
  handleTouchMove(e) {
    if (!this.isSwiping) return
    this.currentX = e.touches[0].clientX
    this.currentY = e.touches[0].clientY

    const deltaX = this.currentX - this.startX
    const deltaY = this.currentY - this.startY

    if (Math.abs(deltaY) > Math.abs(deltaX)) {
      e.preventDefault()
      if (deltaY > 0) {
        this.infosheetTarget.style.transform = `translateY(${deltaY}px)`
      }
    }
  }

  handleTouchEnd() {
    if (!this.isSwiping) return
    const swipeDistance = this.startY + this.currentY
    if (swipeDistance > SWIPE_TRESHOLD) {
      this.infosheetTarget.style.transform = ``
      this.closeInfosheet()
    } else if (swipeDistance < 10) {
      // Reset positie als swipe te kort is
      this.infosheetTarget.style.transform = `translateY(0)`
    } else {
      // Reset positie als swipe te kort is
      this.infosheetTarget.style.transform = `translateY(0)`
    }
  }

  openInfosheet(e) {
    if (this.hasInfosheetTarget) {
      e.preventDefault()
      if (e.params.action) {
        scrollPositionForDialog = window.scrollY
        this.infosheetTurboframeTarget.setAttribute('src', e.params.action)
        this.infosheetTarget.showModal()
        document.body.style.top = `-${scrollPositionForDialog}px`
        document.body.style.position = 'fixed'
        this.infosheetTarget.addEventListener('click', (event) => {
          if (event.target === event.currentTarget) {
            event.stopPropagation()
            this.closeInfosheet()
          }
        })
      } else if (e.params.selector) {
        const sourceElem = document.querySelector(e.params.selector)
        this.sourceElemParent = sourceElem.parentNode
        this.infosheetTurboframeTarget.insertAdjacentElement('beforeEnd', sourceElem)
        this.infosheetTarget.showModal()
      } else if (e.params.extracontent) {
        scrollPositionForDialog = window.scrollY
        this.infosheetTarget.showModal()
        document.body.style.top = `-${scrollPositionForDialog}px`
        document.body.style.position = 'fixed'

        this.infosheetTarget.addEventListener('click', (event) => {
          if (event.target === event.currentTarget) {
            event.stopPropagation()
            this.closeInfosheet()
          }
        })

        const sourceElem = e.currentTarget.querySelector(e.params.extracontent)
        this.sourceElemParent = sourceElem.parentNode
        this.infosheetTurboframeTarget.insertAdjacentElement('beforeEnd', sourceElem)
        if (e.params.header) {
          const header = document.createElement('h4')
          header.textContent = e.params.header
          // Sluitknop
          const button = document.createElement('button')
          button.type = 'button'
          button.classList.add('btn-close--small')
          button.setAttribute('data-action', 'infosheet#closeInfosheet')
          button.innerHTML = `
            <svg width="19" height="19" viewBox="0 0 19 19" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14.7366 13.6794C14.8951 13.8379 14.9841 14.0528 14.9841 14.277C14.9841 14.5012 14.8951 14.7162 14.7366 14.8747C14.5781 15.0332 14.3631 15.1222 14.1389 15.1222C13.9147 15.1222 13.6998 15.0332 13.5413 14.8747L9.07712 10.4091L4.61157 14.8733C4.45306 15.0318 4.23808 15.1208 4.01391 15.1208C3.78975 15.1208 3.57477 15.0318 3.41626 14.8733C3.25775 14.7148 3.1687 14.4998 3.1687 14.2756C3.1687 14.0514 3.25775 13.8365 3.41626 13.6779L7.8818 9.21381L3.41766 4.74826C3.25916 4.58975 3.17011 4.37477 3.17011 4.1506C3.17011 3.92644 3.25916 3.71146 3.41766 3.55295C3.57617 3.39444 3.79116 3.30539 4.01532 3.30539C4.23949 3.30539 4.45447 3.39444 4.61298 3.55295L9.07712 8.01849L13.5427 3.55224C13.7012 3.39374 13.9162 3.30469 14.1403 3.30469C14.3645 3.30469 14.5795 3.39374 14.738 3.55224C14.8965 3.71075 14.9855 3.92574 14.9855 4.1499C14.9855 4.37407 14.8965 4.58905 14.738 4.74756L10.2724 9.21381L14.7366 13.6794Z" fill="black"></path>
            </svg>
          `
          // button.addEventListener('click', () => {
          //   this.closeInfosheet()
          // })

          // Toevoegen
          header.appendChild(button)
          sourceElem.insertBefore(header, sourceElem.firstChild)
          this.injectedHeader = header
        }
      }
      this.infosheetTarget.showModal()
    }
  }

  closeInfosheet() {
    if (this.sourceElemParent) {
      setTimeout(() => this.injectedHeader?.remove(), 400)
      setTimeout(() => (this.injectedHeader = null), 400)
      setTimeout(
        () =>
          this.sourceElemParent.insertAdjacentElement(
            'beforeEnd',
            this.infosheetTurboframeTarget.firstChild
          ),
        400
      )
      setTimeout(() => (this.sourceElemParent = null), 400)
    }
    if (this.hasInfosheetTarget) {
      if (this.infosheetTarget.open) {
        setTimeout(() => (this.infosheetTurboframeTarget.innerHTML = ''), 400)
        this.infosheetTarget.close()
        document.body.style.position = ''
        document.body.style.top = ''
        window.scrollTo({ top: scrollPositionForDialog, left: 0, behavior: 'instant' })
      }
    }
    this.infosheetTarget.removeEventListener('click', (event) => {
      if (event.target === event.currentTarget) {
        event.stopPropagation()
        this.closeInfosheet()
      }
    })
  }
}
