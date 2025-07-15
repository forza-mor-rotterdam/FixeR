import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['form', 'zoekField', 'cancelZoek']

  connect() {
    this.to = null
    this.csrf_token = this.element.querySelector('input[name="csrfmiddlewaretoken"]').value
    this.isSearching()
    this.zoekFieldTarget.addEventListener('input', () => {
      if (this.zoekFieldTarget.value.length === 0) {
        this.zoekFieldTarget.classList.remove('active')
      }
    })
    window.addEventListener('clearSearchForTasks', () => {
      if (this.zoekFieldTarget.value.length !== 0) {
        this.zoekFieldTarget.value = ''
        this.zoekFieldTarget.classList.remove('active')
        this.submit(this.zoekFieldTarget.value)
      }
    })
    screen.orientation.addEventListener('change', () => {
      if (this.zoekFieldTarget.value.length !== 0) {
        this.zoekFieldTarget.value = ''
        this.zoekFieldTarget.classList.remove('active')
        this.submit(this.zoekFieldTarget.value)
      }
    })
  }

  isSearching() {
    const input = this.zoekFieldTarget
    if (this.zoekFieldTarget.value.length !== 0) {
      input.classList.add('active')
      const container = input.closest('.container__search')
      if (container) {
        container.classList.remove('hidden-vertical')
        container.classList.add('show-vertical')
      }
      input.focus()
      input.setSelectionRange(input.value.length, input.value.length)
    } else {
      input.classList.remove('active')
    }
  }

  updateTakenList() {
    let orderChangeEvent = new CustomEvent('searchChangeEvent', {
      bubbles: true,
      cancelable: false,
    })
    this.element.dispatchEvent(orderChangeEvent)
  }
  onChangeHandler(e) {
    clearTimeout(this.to)
    // used for scrolling to last selected task
    sessionStorage.removeItem('selectedTaakId')
    this.to = setTimeout(() => {
      this.submit(this.zoekFieldTarget.value)
    }, 200)

    if (e.target.value.length > 0) {
      this.cancelZoekTarget.classList.remove('hide')
    } else {
      this.cancelZoekTarget.classList.add('hide')
    }
  }

  onCancelSearch() {
    this.zoekFieldTarget.value = ''
    this.cancelZoekTarget.classList.add('hide')
    this.zoekFieldTarget.focus()
    this.to = setTimeout(() => {
      this.submit(this.zoekFieldTarget.value)
    }, 200)
  }

  onSubmit(event) {
    event.preventDefault()
  }

  async submit(q) {
    const zoekUrl = '/taak-zoeken/'
    try {
      const response = await fetch(`${zoekUrl}`, {
        method: 'post',
        headers: {
          'X-CSRFToken': this.csrf_token,
        },
        body: JSON.stringify({
          q: q,
        }),
      })
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`)
      }
      const data = await response.json()
      this.updateTakenList()
      return data.q
    } catch (error) {
      console.error('Error fetching address details:', error.message)
    }
  }
}
