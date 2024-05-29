import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static values = {
    dateObject: String,
  }

  static targets = ['takenLijst']

  selectAll(e) {
    e.preventDefault()
    const checkList = Array.from(this.takenLijstTarget.querySelectorAll('input.form-check-input'))
    const doCheck = e.params.filterType === 'all'
    checkList.forEach((element) => {
      element.checked = doCheck
    })
  }
}
