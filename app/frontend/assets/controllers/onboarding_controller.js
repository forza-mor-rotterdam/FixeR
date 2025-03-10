import { Controller } from '@hotwired/stimulus'

let stadsdeel, wijkenVolledig, wijkenNoord, wijkenZuid, cbList
export default class extends Controller {
  static targets = ['form', 'stadsdeel', 'taaktypeInput']

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

  taaktypeInputTargetConnected(element) {
    const button = document.createElement('button')
    button.setAttribute('class', 'btn btn-inline btn-info')
    button.setAttribute('type', 'button')
    button.setAttribute('data-action', 'infosheet#openInfosheet')
    button.setAttribute('data-infosheet-action-param', `/taaktype/${element.value}/taakr`)
    button.setAttribute('aria-label', 'meer info')
    button.innerHTML = `<img src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTQiIGhlaWdodD0iMTUiIHZpZXdCb3g9IjAgMCAxNCAxNSIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTcgMC43NzczNDRDNS4xNDM4MSAwLjc3NzM0NCAzLjM2MzQzIDEuNTE0ODcgMi4wNTAxNSAyLjgyNzQ5QzAuNzM3NTEyIDQuMTQwNyAwIDUuOTIxMTUgMCA3Ljc3NzM0QzAgOS42MzM1NCAwLjczNzUyNyAxMS40MTM5IDIuMDUwMTUgMTIuNzI3MkMzLjM2MzM1IDE0LjAzOTggNS4xNDM4MSAxNC43NzczIDcgMTQuNzc3M0M4Ljg1NjIgMTQuNzc3MyAxMC42MzY2IDE0LjAzOTggMTEuOTQ5OSAxMi43MjcyQzEzLjI2MjUgMTEuNDE0IDE0IDkuNjMzNTQgMTQgNy43NzczNEMxNCA1LjkyMTE1IDEzLjI2MjUgNC4xNDA3NyAxMS45NDk5IDIuODI3NDlDMTAuNjM2NiAxLjUxNDg2IDguODU2MiAwLjc3NzM0NCA3IDAuNzc3MzQ0Wk03IDMuMjM3MjhDNy4yNDIyIDMuMjM3MjggNy40NzQ2NiAzLjMzMzcxIDcuNjQ2MjcgMy41MDQ3NEM3LjgxNzg4IDMuNjc2MzYgNy45MTQzIDMuOTA4ODEgNy45MTM3MyA0LjE1MTU4QzcuOTE0MyA0LjM5Mzc5IDcuODE3ODggNC42MjYyNSA3LjY0NjI3IDQuNzk3ODVDNy40NzQ2NSA0Ljk2ODg5IDcuMjQyMiA1LjA2NTMxIDcgNS4wNjUzMUM2Ljc1NzggNS4wNjUzMSA2LjUyNTM0IDQuOTY4ODkgNi4zNTM3MyA0Ljc5Nzg1QzYuMTgyMTIgNC42MjYyMyA2LjA4NTcgNC4zOTM3OSA2LjA4NjI3IDQuMTUxNThDNi4wODU3IDMuOTA4ODEgNi4xODIxMiAzLjY3NjM1IDYuMzUzNzMgMy41MDQ3NEM2LjUyNTM1IDMuMzMzNyA2Ljc1NzggMy4yMzcyOCA3IDMuMjM3MjhaTTcgNi4yMDg2OUM3LjQ4MDk3IDYuMjA4NjkgNy44Njc4MSA2LjU5NTU0IDcuODY3ODEgNy4wNzY1MVYxMS40NDk1QzcuODY3ODEgMTEuOTMwNSA3LjQ4MDk3IDEyLjMxNzMgNyAxMi4zMTczQzYuNTE5MDMgMTIuMzE3MyA2LjEzMjE5IDExLjkzMDUgNi4xMzIxOSAxMS40NDk1VjcuMDc2NTFDNi4xMzIxOSA2LjU5NTU0IDYuNTE5MDMgNi4yMDg2OSA3IDYuMjA4NjlaIiBmaWxsPSIjMDA4MTFmIi8+Cjwvc3ZnPgo='>`
    element.parentElement.appendChild(button)
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
