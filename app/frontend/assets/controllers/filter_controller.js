import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = [
    'foldoutStatesField',
    'filterInput',
    'cancelZoek',
    'zoekField',
    'pageField',
    'selectedChoicesCount',
    'selectedChoicesTotalCount',
    'takenKaart',
    'kaartModusOption',
    'taakPopup',
  ]
  static values = {
    activeFilterCount: String,
  }
  initialize() {
    this.kaartModus = null
    console.log(this.identifier)
    this.element[this.identifier] = this
    let childControllerConnectedEvent = new CustomEvent('childControllerConnectedEvent', {
      bubbles: true,
      cancelable: false,
      detail: {
        controller: this,
      },
    })
    this.cancelZoekTarget.classList[this.zoekFieldTarget.value.length > 0 ? 'remove' : 'add'](
      'hide'
    )
    window.dispatchEvent(childControllerConnectedEvent)
    this.updateSelectedChoicesCount()
  }
  connect() {
    // console.log('connect: this.takenKaartTarget.takenKaart, ', this.takenKaartTarget.takenKaart)
  }
  updateSelectedChoicesCount() {
    this.selectedChoicesCountTargets.map((elem) => {
      let container = elem.closest('details.filter')
      if (!container || container.classList.contains('filter--active')) {
        container = elem.closest('form')
      }
      elem.textContent = `${
        Array.from(container.querySelectorAll('li.filter-option-container input:checked')).length
      }`
    })
  }
  removeFilter(e) {
    const input = document.querySelector(`[name="${e.params.name}"][value="${e.params.value}"]`)
    input.checked = false
    this.updateSelectedChoicesCount()
  }
  onChangeFilter() {
    this.updateSelectedChoicesCount()
    this.element.requestSubmit()
  }
  selectAll(e) {
    const checkList = Array.from(e.target.closest('details').querySelectorAll('.form-check-input'))
    const doCheck = e.params.filterType === 'all'
    checkList.forEach((element) => {
      element.checked = doCheck
    })
    this.updateSelectedChoicesCount()
  }

  removeAllFilters() {
    this.filterInputTargets.checked = false
    this.filterInputTargets.forEach((input) => {
      input.checked = false
    })
    this.updateSelectedChoicesCount()
  }
  onCancelSearch() {
    this.zoekFieldTarget.value = ''
    this.cancelZoekTarget.classList.add('hide')
    this.zoekFieldTarget.focus()
    this.to = setTimeout(() => {
      this.element.requestSubmit()
    }, 200)
  }
  onSearchChangeHandler(e) {
    clearTimeout(this.to)
    // used for scrolling to last selected task
    sessionStorage.removeItem('selectedTaakId')
    this.to = setTimeout(() => {
      this.element.requestSubmit()
    }, 200)

    this.cancelZoekTarget.classList[e.target.value.length > 0 ? 'remove' : 'add']('hide')
  }
  onSortingChangeHandler() {
    this.element.requestSubmit()
  }
  onGPSChangeHandler(e) {
    console.log('onGPSChangeHandler: ', e.target)
  }
  onPageClickEvent(e) {
    this.pageFieldTarget.value = e.params.page
    this.element.requestSubmit()
    this.pageFieldTarget.value = 1
  }
  kaartModusOptionClickHandler(e) {
    const li = e.target.closest('li')
    Array.from(e.target.closest('ul').querySelectorAll('li')).map((elem) => {
      elem.classList[li == elem ? 'add' : 'remove']('active')
    })
    this.kaartModus = e.target.value
    this.takenKaartTarget?.takenKaart?.kaartModusChangeHandler(this.kaartModus)
    this.element.requestSubmit()
  }
  takenKaartTargetConnected() {
    setTimeout(() => {
      this.takenKaartTarget?.takenKaart?.kaartModusChangeHandler(this.kaartModus)
    }, 1)
  }
  kaartModusOptionTargetConnected(kaartModusOption) {
    this.kaartModus = kaartModusOption.checked ? kaartModusOption.value : this.kaartModus
  }
}
