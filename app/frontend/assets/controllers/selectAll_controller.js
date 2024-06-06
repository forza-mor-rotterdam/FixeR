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
    console.log('checklist length', checkList.length)
    const doCheck = e.params.filterType === 'all'
    checkList.forEach((element) => {
      element.querySelector('input[type="checkbox"]').checked = doCheck
    })
    const checkedItems = e.target.closest('.form-row').querySelectorAll('input:checked')
    this.addNumber(e.target.closest('.form-row').querySelector('.label'), checkedItems.length)
  }

  addNumber(target, n) {
    let span = target.querySelector('span')
    if (!span) {
      span = document.createElement('span')
      span.classList.add('count')
      target.appendChild(span)
    }
    span.textContent = n
  }
}
