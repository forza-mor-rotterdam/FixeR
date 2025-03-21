import { Controller } from '@hotwired/stimulus'

const MAX_CHARACTERS = 100
export default class extends Controller {
  static targets = ['content']

  connect() {
    this.element.controller = this
    this.manager = null
    this.contentString = null
    this.truncatedString = null
    if (this.hasContentTarget) {
      this.contentString = this.contentTarget.innerHTML
      if (this.contentString.length > MAX_CHARACTERS) {
        this.truncatedString = `${this.contentString.slice(
          0,
          MAX_CHARACTERS - 13
        )}... <a href="" role="button" data-action="notificaties--snack-overzicht-item#readMore">Lees meer</a>`
        this.contentTarget.innerHTML = this.truncatedString
        setTimeout(() => {
          this.contentTarget.style.height = `${this.contentTarget.clientHeight}px`
          this.initialHeight = this.contentTarget.clientHeight
        }, 500)
      }
    }
  }
  initializeManager(manager) {
    this.manager = manager
  }
  markeerAlsGelezen() {
    this.element.classList.add('is-watched')
  }
  readMore(e = null) {
    e?.preventDefault()
    this.contentTarget.innerHTML = `${this.contentString} <a href="" role="button" data-action="notificaties--snack-overzicht-item#readLess">Lees minder</a>`
    this.contentTarget.style.height = `${this.contentTarget.scrollHeight}px`
  }
  readLess(e = null) {
    e?.preventDefault()
    this.contentTarget.innerHTML = this.truncatedString
    this.contentTarget.style.height = `${this.initialHeight}px`
  }
}
