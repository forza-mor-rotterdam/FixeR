import { Controller } from '@hotwired/stimulus'

// const PDOK_WIJKEN = []
let noordWijken
let zuidWijken
export default class extends Controller {
  static values = {
    dateObject: String,
  }

  connect() {
    console.log('Connecting Werklocatie')
  }
  updateWijken(e) {
    const wijken = e.params.wijken
    const stadsdeel = e.target.value.toLowerCase()
    // let unSelectedWijken = []
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
    console.log('wijken noord', noordWijken)
    console.log('wijken zuid', zuidWijken)

    if (stadsdeel) {
      if (stadsdeel.toLowerCase() === 'volledig') {
        this.element.querySelector('h3.label').textContent = 'Wijken voor heel Rotterdam'
      } else {
        const capt = stadsdeel.charAt(0).toUpperCase() + stadsdeel.slice(1)
        this.element.querySelector('h3.label').textContent = `Wijken in ${capt}`
      }

      const cbList = this.element.querySelectorAll('input[type=checkbox]')

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
      this.element.querySelector('.container__wijkenlijst').classList.remove('visually-hidden')
    }
  }
}
