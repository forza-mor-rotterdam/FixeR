import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  static targets = ['infosheet']

  connect() {
    console.log('__infosheet connected__')
  }

  openInfosheet(e) {
    console.log('open infosheet', this.infosheetTarget)
    if (this.hasInfosheetTarget) {
      console.log('open infosheet', this.infosheetTarget)
      e.preventDefault()
      // this.turboframeTarget.setAttribute('src', e.params.action)
      this.infosheetTarget.showModal()
    }
    document.body.style.overflow = 'hidden'
  }

  closeInfosheet() {
    if (this.hasInfosheetTarget) {
      if (this.infosheetTarget.open) {
        this.infosheetTarget.close()
      }
    }
    document.body.style.overflow = ''
  }
}
