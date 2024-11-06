import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['title', 'subTitle', 'infoExtra', 'turboFrame', 'closeModalElement', 'taakItem']

  initialize() {
    document.body.classList.remove('show-modal')

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        this.closeModal()
      }
    })

    addEventListener('openModalFromMap', (e) => {
      if (this.element.closest('.list-item')) {
        if (this.element.closest('.list-item').classList.contains('selected')) {
          this.openModal(e)
        }
      }
    })
  }

  closeModalElementTargetConnected(element) {
    let self = this
    if (element.dataset.turboFrameId) {
      let turboElement = document.getElementById(element.dataset.turboFrameId)
      turboElement.src = element.dataset.turboFrameSrc
      self.closeModal()
      turboElement.reload()
    }
  }
  closeModal() {
    let self = this
    if (self.hasTaakItemTarget) {
      self.taakItemTarget.classList.remove('active', 'selected')
      self.taakItemTarget.classList.add('highlight-once')
      setTimeout(() => {
        self.taakItemTarget.classList.remove('highlight-once')
      }, 2000)
    }
    const modalList = self.element.querySelectorAll('.modal')
    const modalBackdrop = self.element.querySelector('.modal-backdrop')
    if (self.hasTurboFrameTarget) {
      self.turboFrameTarget.innerHTML = ''
    }

    modalList.forEach((modal) => {
      modal.classList.remove('show')
    })
    modalBackdrop.classList.remove('show')
    document.body.classList.remove('show-modal', 'show-modal--transparent', 'show-navigation')
  }
  openModal(event) {
    event.preventDefault()
    const params = event.params || event.detail.e.params
    let self = this

    if (params.taakid) {
      sessionStorage.setItem('selectedTaakId', params.taakid)
    }

    if (self.hasTitleTarget) {
      self.titleTarget.innerHTML = params.title
    }
    if (self.hasSubTitleTarget) {
      if (params.subTitle) {
        self.subTitleTarget.innerHTML = params.subTitle
      } else {
        self.subTitleTarget.style.display = 'none'
      }
    }
    if (self.hasInfoExtraTarget) {
      if (params.infoExtra) {
        self.infoExtraTarget.innerHTML = params.infoExtra
      } else {
        self.infoExtraTarget.style.display = 'none'
      }
    }
    let modal = this.element.querySelector('.modal')
    if (self.hasTurboFrameTarget) {
      self.turboFrameTarget.id = params.id
      self.turboFrameTarget.src = params.url
      modal = self.turboFrameTarget.closest('.modal')
    }
    const modalBackdrop = modal.querySelector('.modal-backdrop')
    modal.classList.add('show')
    modalBackdrop.classList.add('show')
    let classes = ''
    if (event.params && event.params.type === 'navigation') {
      classes = 'show-navigation'
      // used for scrolling to last selected task
      sessionStorage.removeItem('selectedTaakId')
    } else {
      classes = 'show-modal'
    }
    document.body.classList.add(classes)
  }
}
