import { Controller } from '@hotwired/stimulus'
import { renderStreamMessage } from '@hotwired/turbo'

export default class extends Controller {
  static targets = [
    'modal',
    'modalSluiten',
    'template',
    'dialog',
    'content',
    'header',
    'body',
    'footer',
    'kaartLarge',
    'toplevelContainer',
  ]

  connect() {}

  openModal(e) {
    e.preventDefault()
    this.abortController = new AbortController()
    this.params = e.params
    if (!this.hasTemplateTarget || !this.hasModalTarget) {
      return
    }
    const templateClone = this.getCloneModalTemplate()
    this.modalTarget.appendChild(templateClone)
  }
  fetchModalContent(action) {
    fetch(action, { signal: this.abortController.signal })
      .then((response) => response.text())
      .then((text) => renderStreamMessage(text))
      .catch(function (err) {
        console.error(` Err: ${err}`)
      })
  }
  contentTargetConnected() {
    document.body.classList.add('show-dialog')
    console.log('CLONE')
    if (this.params.action) {
      this.fetchModalContent(this.params.action)
    } else if (this.params.content) {
      this.contentTarget.innerHTML = ''
      this.contentTarget.insertAdjacentHTML('beforeend', this.params.content)
    }

    this.dialogTarget.showModal()
    if (this.params.showMap) {
      document.querySelector('#modal_close_button').blur()
    }

    this.dialogTarget.addEventListener('cancel', (e) => {
      e.preventDefault()
      this.closeModal()
    })
    requestAnimationFrame(() => {
      if (this.params.cssClass) {
        this.dialogTarget.classList.add(...this.params.cssClass.split(' '))
      }
      this.dialogTarget.classList.add('fade-in')
    })

    this.dialogTarget.addEventListener('click', (event) => {
      var rect = this.dialogTarget.getBoundingClientRect()
      var isInDialog =
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width

      if (event.screenX != 0 && event.screenY != 0 && !isInDialog) {
        this.closeModal()
      }
    })
  }
  getCloneModalTemplate() {
    return this.templateTarget.content.cloneNode(true)
  }

  turboActionModalTargetConnected(target) {
    this.turboActionModalTargetClone = target.cloneNode(true)
  }
  closeModal() {
    this.abortController.abort()
    this.dialogTarget.classList.remove('fade-in')
    if (this.params.showMap) {
      this.hideMapLarge()
    }
    setTimeout(() => {
      document.body.classList.remove('show-dialog')
      if (this.hasDialogTarget) {
        this.dialogTarget.remove()
      }
    }, 300)
  }
  modalSluitenTargetConnected() {
    this.closeModal()
  }

  elementContentHeight(elem) {
    return Array.from(elem.children).reduce((total, elem) => {
      const style = window.getComputedStyle(elem)
      const height = ['top', 'bottom']
        .map(function (side) {
          return parseInt(style['margin-' + side], 10)
        })
        .reduce(function (t, side) {
          return t + side
        }, elem.getBoundingClientRect().height)

      return (total += height)
    }, 0)
  }
}
