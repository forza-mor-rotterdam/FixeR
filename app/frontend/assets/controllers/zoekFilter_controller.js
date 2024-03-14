import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['form', 'zoekField']

  connect() {
    let orderChangeEvent = new CustomEvent('orderChangeEvent', {
      bubbles: true,
      cancelable: false,
      detail: { order: this.zoekFieldTarget.value },
    })
    console.log(this.zoekFieldTarget)
    console.log(this.formTarget)
    const initialValue = this.zoekFieldTarget.value
    const searchInput = document.querySelector('input[type=search]')
    searchInput.value = initialValue
    console.log({ searchInput })
    searchInput.addEventListener('search', function () {
      console.log('Searching on searchInput')
      self.element.requestSubmit()
    })
    this.element.dispatchEvent(orderChangeEvent)
  }
  onChangeHandler() {
    console.log('CHANGING')
    console.log(this.formTarget)
    console.log(this.zoekFieldTarget)
    this.formTarget.requestSubmit()
  }
}
