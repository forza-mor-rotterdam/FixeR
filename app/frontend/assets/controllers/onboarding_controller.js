import { Controller } from '@hotwired/stimulus'

let currentLabel, checkedItems, stadsdeel, wijken, noordWijken, zuidWijken, cbList
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
    if (currentLabel && checkedItems) {
      let span = currentLabel.querySelector('span')
      console.log('span', span)
      if (!span) {
        span = document.createElement('span')
        span.classList.add('count')
        currentLabel.appendChild(span)
      }
      span.textContent = checkedItems.length
    }
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
        this.element.querySelector('h3.label').textContent = 'Wijken voor heel Rotterdam'
      } else {
        const capt = stadsdeel.charAt(0).toUpperCase() + stadsdeel.slice(1)
        this.element.querySelector('h3.label').textContent = `Wijken in ${capt}`
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
      this.element.querySelector('.container__wijkenlijst').classList.remove('hidden')
      this.addNumber()
    }
  }
}
