import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['foldoutStatesField', 'filterInput', 'cancelZoek', 'zoekField', 'pageField']
  static values = {
    activeFilterCount: String,
  }
  initialize() {
    let self = this
    console.log(self.identifier)
    self.element[self.identifier] = self
    let childControllerConnectedEvent = new CustomEvent('childControllerConnectedEvent', {
      bubbles: true,
      cancelable: false,
      detail: {
        controller: self,
      },
    })
    this.cancelZoekTarget.classList[this.zoekFieldTarget.value.length > 0 ? 'remove' : 'add'](
      'hide'
    )
    window.dispatchEvent(childControllerConnectedEvent)
  }
  removeFilter(e) {
    const input = document.querySelector(`[id="${e.params.code}"]`)
    input.checked = false
    this.element.requestSubmit()
  }
  toggleActiveFilter(e) {
    e.preventDefault()
    const input = this.foldoutStatesFieldTarget
    let idArray = JSON.parse(input.value)
    const idAttr = e.target.getAttribute('id')
    const isOpen = e.target.hasAttribute('open')
    let index = idArray.indexOf(idAttr)
    if (index > -1) {
      idArray.splice(index, 1)
    }
    if (isOpen) {
      idArray.push(idAttr)
    }
    input.value = JSON.stringify(idArray)
  }
  onChangeFilter() {
    this.element.requestSubmit()
  }
  selectAll(e) {
    const checkList = Array.from(e.target.closest('details').querySelectorAll('.form-check-input'))
    const doCheck = e.params.filterType === 'all'
    checkList.forEach((element) => {
      element.checked = doCheck
    })
  }

  removeAllFilters() {
    this.filterInputTargets.checked = false
    this.filterInputTargets.forEach((input) => {
      input.checked = false
    })
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
  onPageClickEvent(e) {
    console.log(e.params.page)
    this.pageFieldTarget.value = e.params.page
    this.element.requestSubmit()
    this.pageFieldTarget.value = 1
  }
  kaartModusOptionClickHandler() {
    this.element.requestSubmit()
  }
}
