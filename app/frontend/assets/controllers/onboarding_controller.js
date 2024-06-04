import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['form']
  onComplete(e) {
    e.preventDefault()
    this.element.classList.add('complete')
    setTimeout(() => {
      this.formTarget.requestSubmit()
    }, 4000)
  }
}
