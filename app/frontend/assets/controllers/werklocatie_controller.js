import { Controller } from '@hotwired/stimulus'

let stadsdeel
let wijken
let noordWijken
let zuidWijken
let cbList
// let numberChecked = 0
export default class extends Controller {
  static values = {
    dateObject: String,
  }

  connect() {
    if (this.element.querySelector('select').value) {
      this.stadsdeel = this.element.querySelector('select').value
      this.updateWijken()
      this.getCheckedItems()
    }
    console.log('cbList', cbList)
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
      this.element.querySelector('.container__wijkenlijst').classList.remove('hidden')
    }
  }

  getCheckedItems() {
    const checkedList = cbList.querySelectorAll('input[type=checkbox]:checked')
    console.log(checkedList.length, checkedList)
  }
}
