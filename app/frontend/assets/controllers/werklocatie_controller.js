import { Controller } from '@hotwired/stimulus'

// const PDOK_WIJKEN = []
export default class extends Controller {
  static values = {
    dateObject: String,
  }

  connect() {
    console.log('Connecting Werklocatie')
  }
  updateWijken(e) {
    const wijken = e.params.wijken
    const stadsdeel = e.target.value
    // let unSelectedWijken = []
    let wijkenChoices = []
    let sortedPdokWijken = wijken.slice().sort((a, b) => a.wijknaam.localeCompare(b.wijknaam))

    if (stadsdeel) {
      console.log('stadsdeel: ', stadsdeel)
      if (stadsdeel.toLowerCase() === 'volledig') {
        // unSelectedWijken = []
        let noordWijken = sortedPdokWijken
          .filter((wijk) => wijk.stadsdeel.toLowerCase() === 'noord')
          .map((wijk) => [wijk.wijkcode, wijk.wijknaam])
        let zuidWijken = sortedPdokWijken
          .filter((wijk) => wijk.stadsdeel.toLowerCase() === 'zuid')
          .map((wijk) => [wijk.wijkcode, wijk.wijknaam])

        if (noordWijken.length > 0) {
          wijkenChoices.push(['Noord', noordWijken])
        }
        if (zuidWijken.length > 0) {
          wijkenChoices.push(['Zuid', zuidWijken])
        }

        this.element.querySelectorAll('label')[1].textContent = 'Wijken voor heel Rotterdam'
      } else {
        // unSelectedWijken = sortedPdokWijken
        // .filter((wijk) => wijk.stadsdeel.toLowerCase() !== stadsdeel.toLowerCase())
        // .map((wijk) => [wijk.wijkcode, wijk.wijknaam])
        this.element.querySelectorAll('label')[1].textContent = `Wijken in ${stadsdeel}`
      }
      // console.log('NIET geselecteerde wijken', unSelectedWijken)

      // unSelectedWijken.forEach((element) => {
      //   console.log('niet geselecteerd: ', element)
      // })
      // wijkenChoices.forEach((element) => {
      //   console.log('wel geselecteerd: ', element)
      // })

      const fieldsList = this.element.querySelectorAll(':scope > ul > li')
      fieldsList.forEach((element) => {
        if (stadsdeel === 'volledig') {
          element.classList.remove('hidden')
        } else {
          if (element.firstChild.nodeValue.toLowerCase() !== stadsdeel) {
            const list = element.querySelectorAll('input[type=checkbox]')
            list.forEach((cb) => {
              cb.checked = false
            })
            element.classList.add('hidden')
          } else {
            element.classList.remove('hidden')
          }
        }
      })

      // this.fields['wijken'].choices = wijkenChoices
    }
  }
}
