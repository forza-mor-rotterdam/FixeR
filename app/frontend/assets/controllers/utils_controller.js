import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['breedte']

  breedteTargetConnected(elem) {
    elem.textContent = window.innerWidth
  }

  goToUrl(e) {
    window.location.href = e.params.url
  }

  foldOut() {
    this.element.classList.toggle('show')
  }
}
