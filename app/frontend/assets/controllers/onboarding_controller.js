import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['form']

  onNext() {
    setTimeout(() => {
      window.scrollTo(0, 0)
    }, 100)
  }

  onComplete(e) {
    e.preventDefault()
    console.log('onComplete')
    this.element.closest('turbo-frame').classList.add('complete')
    setTimeout(() => {
      this.formTarget.requestSubmit()
    }, 5000)
  }
}
