import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['form']

  onNext() {
    setTimeout(() => {
      window.scrollTo(0, 0)
    }, 100)
  }
  selectTask(e) {
    const checkedItems = e.target.closest('.form-row').querySelectorAll('input:checked')
    console.log('checkedItems', checkedItems.length)
    console.log(e.target.closest('.form-row').querySelector('.label'))
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
