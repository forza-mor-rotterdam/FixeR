import { Controller } from '@hotwired/stimulus'

let stadsdeel, wijkenVolledig, wijkenNoord, wijkenZuid, cbList
export default class extends Controller {
  static targets = ['form', 'stadsdeel']

  connect() {
    this.updateCounters()

    if (this.hasStadsdeelTarget) {
      this.sortAndSaveWijken()
      if (this.element.querySelector('input[type=radio]:checked')) {
        stadsdeel = this.element.querySelector('input[type=radio]:checked').value
      }

      if (stadsdeel) {
        this.updateWijken()
      }
    }
    this.element.closest('turbo-frame').classList.remove('complete')
  }

  updateCounters() {
    const countersToShow = this.element.querySelectorAll('.count')
    countersToShow.forEach((counter) => {
      const formRow = counter.closest('.form-row')
      const number = formRow.querySelectorAll('input:checked').length
      counter.textContent = number
    })
  }

  onNext() {
    setTimeout(() => {
      window.scrollTo(0, 0)
    }, 100)
  }

  onComplete(e) {
    e.preventDefault()
    this.element.closest('turbo-frame').classList.add('complete')
    setTimeout(() => {
      this.onSubmit()
    }, 3500)
  }

  onSubmit() {
    this.formTarget.requestSubmit()
  }

  sortAndSaveWijken() {
    wijkenVolledig = JSON.parse(
      this.element.querySelectorAll('input[type=radio]')[0].dataset['onboardingWijkenParam']
    )
    let wijkenVolledigSorted = wijkenVolledig
      .slice()
      .sort((a, b) => a.wijknaam.localeCompare(b.wijknaam))
    wijkenNoord = wijkenVolledigSorted
      .filter((wijk) => wijk.stadsdeel.toLowerCase() === 'noord')
      .map((wijk) => wijk.wijkcode)
    wijkenZuid = wijkenVolledigSorted
      .filter((wijk) => wijk.stadsdeel.toLowerCase() === 'zuid')
      .map((wijk) => wijk.wijkcode)
  }

  updateWijken(e = null) {
    if (e) {
      stadsdeel = e.target.value.toLowerCase()
    }

    if (stadsdeel.toLowerCase() === 'volledig') {
      this.element.querySelector('h3.label span').innerHTML = 'Wijken in heel Rotterdam'
    } else {
      const capt = stadsdeel.charAt(0).toUpperCase() + stadsdeel.slice(1)
      this.element.querySelector('h3.label span').innerHTML = `Wijken in ${capt}`
    }

    cbList = this.element.querySelectorAll('input[type=checkbox]')

    cbList.forEach((cb) => {
      if (stadsdeel === 'noord') {
        if (wijkenZuid.includes(cb.value)) {
          cb.checked = false
          cb.closest('li').style.display = 'none'
        } else {
          cb.closest('li').style.display = 'block'
        }
      } else if (stadsdeel === 'zuid') {
        if (wijkenNoord.includes(cb.value)) {
          cb.checked = false
          cb.closest('li').style.display = 'none'
        } else {
          cb.closest('li').style.display = 'block'
        }
      } else {
        cb.closest('li').style.display = 'block'
      }
    })
    this.element.querySelector('.container__wijkenlijst').classList.remove('hidden')
    this.updateCounters()
  }
}
