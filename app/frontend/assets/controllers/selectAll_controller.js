import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static values = {
    dateObject: String,
  }

  selectAll(e) {
    e.preventDefault()
    const checkList = Array.from(
      e.target
        .closest('.form-row')
        .querySelectorAll('li:not([style*="display:none"]):not([style*="display: none"]')
    )
    const doCheck = e.params.filterType === 'all'
    checkList.forEach((element) => {
      element.querySelector('input[type="checkbox"]').checked = doCheck
    })
  }
}
