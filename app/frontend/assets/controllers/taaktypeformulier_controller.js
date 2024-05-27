import { Controller } from '@hotwired/stimulus'
import $ from 'jquery' // Import jQuery
// eslint-disable-next-line no-unused-vars
import Select2 from 'select2'

let form = null
let inputList = null
// eslint-disable-next-line no-unused-vars
let formData = null
export default class extends Controller {
  static targets = ['formTaaktype', 'voorbeeldWel', 'voorbeeldNiet']

  initializeSelect2() {
    const afdelingen = this.formTaaktypeTarget.querySelector('#afdelingen_1')
    const middelen = this.formTaaktypeTarget.querySelector('#taaktypemiddelen_1')
    const volgend_select = this.formTaaktypeTarget.querySelector('#volgende_taaktypes_1')
    const gerelateerde_onderwerpen_select = this.formTaaktypeTarget.querySelector(
      '#gerelateerde_onderwerpen_1'
    )
    const gerelateerde_taaktypes_select = this.formTaaktypeTarget.querySelector(
      '#gerelateerde_taaktypes_1'
    )

    this.doSelect2(afdelingen, 'Zoek op afdeling')
    this.doSelect2(middelen, 'Zoek op materieel')
    this.doSelect2(volgend_select, 'Zoek op taaktype')
    this.doSelect2(gerelateerde_onderwerpen_select, 'Zoek op onderwerp')
    this.doSelect2(gerelateerde_taaktypes_select, 'Zoek op taaktype')
  }

  connect() {
    form = this.formTaaktypeTarget
    inputList = document.querySelectorAll('[type="text"]')
    this.defaultErrorMessage = 'Vul a.u.b. dit veld in.'

    formData = new FormData(form)
    this.initializeSelect2()

    for (const input of inputList) {
      const error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]

      input.addEventListener('input', () => {
        if (input.validity.valid) {
          input.closest('.form-row').classList.remove('is-invalid')
          error.textContent = ''
        } else {
          error.textContent = this.defaultErrorMessage
          input.closest('.form-row').classList.add('is-invalid')
        }
      })
    }
  }

  doSelect2(element, placeholder = 'Zoek op') {
    $(element).select2({ placeholder: placeholder })
    this.setNotRequiredSelect2(element)
  }

  setNotRequiredSelect2(s2Element) {
    const small = document.createElement('small')
    small.textContent = '(Niet verplicht)'
    const required = s2Element.closest('.form-row').querySelector('select').hasAttribute('required')
    if (!required) {
      s2Element.closest('.form-row').querySelector('label').appendChild(small)
    }
  }

  addExample(e) {
    const examples = e.target.parentNode.querySelectorAll('.hide')
    if (examples.length > 0) {
      examples[0].classList.remove('hide')
      if (e.target.parentNode.querySelectorAll('.hide').length === 0) {
        e.target.classList.add('hide')
      }
    }
  }
}
