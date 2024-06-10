import { Controller } from '@hotwired/stimulus'

let currentLabel, stadsdeel, wijken, noordWijken, zuidWijken, cbList
let checkedItems = 0
export default class extends Controller {
  static targets = ['form', 'stadsdeel']

  connect() {
    if (this.hasStadsdeelTarget) {
      if (this.stadsdeelTarget.value) {
        this.stadsdeel = this.element.querySelector('select').value
        this.updateWijken()
      }
    }
  }

  onNext() {
    setTimeout(() => {
      window.scrollTo(0, 0)
    }, 100)
  }
  selectTask(e) {
    checkedItems = e.target.closest('.form-row').querySelectorAll('input:checked')
    currentLabel = e.target.closest('.form-row').querySelector('.label')
    this.addNumber()
  }

  onComplete(e) {
    e.preventDefault()
    this.element.closest('turbo-frame').classList.add('complete')
    setTimeout(() => {
      this.formTarget.requestSubmit()
    }, 5000)
  }

  addNumber() {
    currentLabel.querySelector('i').textContent = checkedItems.length
  }

  updateWijken(e) {
    if (e) {
      wijken = e.params.wijken
      stadsdeel = e.target.value.toLowerCase()
    }
    let wijkenChoices = []
    let sortedPdokWijken = wijken.slice().sort((a, b) => a.wijknaam.localeCompare(b.wijknaam))
    noordWijken = sortedPdokWijken
      .filter((wijk) => wijk.stadsdeel.toLowerCase() === 'noord')
      .map((wijk) => wijk.wijkcode)
    zuidWijken = sortedPdokWijken
      .filter((wijk) => wijk.stadsdeel.toLowerCase() === 'zuid')
      .map((wijk) => wijk.wijkcode)

    if (noordWijken.length > 0) {
      wijkenChoices.push(['Noord', noordWijken])
    }
    if (zuidWijken.length > 0) {
      wijkenChoices.push(['Zuid', zuidWijken])
    }

    if (stadsdeel) {
      if (stadsdeel.toLowerCase() === 'volledig') {
        this.element.querySelector('h3.label span').innerHTML = 'Wijken voor heel Rotterdam'
      } else {
        const capt = stadsdeel.charAt(0).toUpperCase() + stadsdeel.slice(1)
        this.element.querySelector('h3.label span').innerHTML = `Wijken in ${capt}`
      }

      cbList = this.element.querySelectorAll('input[type=checkbox]')

      cbList.forEach((cb) => {
        if (stadsdeel === 'noord') {
          if (zuidWijken.includes(cb.value)) {
            cb.checked = false
            cb.closest('li').style.display = 'none'
          } else {
            cb.closest('li').style.display = 'block'
          }
        } else if (stadsdeel === 'zuid') {
          if (noordWijken.includes(cb.value)) {
            cb.checked = false
            cb.closest('li').style.display = 'none'
          } else {
            cb.closest('li').style.display = 'block'
          }
        } else {
          cb.closest('li').style.display = 'block'
        }
      })
      checkedItems = this.element.querySelectorAll('input:checked')
      console.log(e.target)
      currentLabel = this.element.querySelector('.container__wijkenlijst .label')
      this.element.querySelector('.container__wijkenlijst').classList.remove('hidden')
      this.addNumber()
    }
  }
}
