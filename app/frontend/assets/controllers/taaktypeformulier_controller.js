import { Controller } from '@hotwired/stimulus'
import $ from 'jquery' // Import jQuery
// eslint-disable-next-line no-unused-vars
import Select2 from 'select2'

let form = null
let inputList = null
// eslint-disable-next-line no-unused-vars
let formData = null
export default class extends Controller {
  static targets = ['formTaaktype']

  initializeSelect2() {
    const volgend_select = this.formTaaktypeTarget.querySelector('#volgende_taaktypes_1')
    const gerelateerd_select = this.formTaaktypeTarget.querySelector('#gerelateerde_onderwerpen_1')
    $(volgend_select).select2({})
    $(gerelateerd_select).select2({})
    $().select2({})

    $(volgend_select).on('select2:select', function (e) {
      const select = e.target
      const error = select.closest('.form-row').getElementsByClassName('invalid-text')[0]

      if (select.validity.valid) {
        select.closest('.form-row').classList.remove('is-invalid')
        error.textContent = ''
      } else {
        error.textContent = this.defaultErrorMessage
        select.closest('.form-row').classList.add('is-invalid')
      }
    })
    $(gerelateerd_select).on('select2:select', function (e) {
      const select = e.target
      const error = select.closest('.form-row').getElementsByClassName('invalid-text')[0]

      if (select.validity.valid) {
        select.closest('.form-row').classList.remove('is-invalid')
        error.textContent = ''
      } else {
        error.textContent = this.defaultErrorMessage
        select.closest('.form-row').classList.add('is-invalid')
      }
    })
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

    // form.addEventListener('submit', (event) => {
    //   const allFieldsValid = this.checkValids()

    //   if (!allFieldsValid) {
    //     const errorList = document.querySelectorAll('div.is-invalid')
    //     errorList[0].scrollIntoView({ behavior: 'smooth' })
    //     event.preventDefault()
    //   }
    // })
  }

  // checkValids() {
  //   const inputList = document.querySelectorAll('input[type="text"], select')
  //   let count = 0
  //   for (const input of inputList) {
  //     let error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]
  //     let invalid = input.value.length == 0 && input.hasAttribute('required')
  //     error.textContent = invalid ? this.defaultErrorMessage : ''
  //     input.closest('.form-row').classList[invalid ? 'add' : 'remove']('is-invalid')
  //     if (invalid) {
  //       count++
  //     }
  //   }
  //   return count === 0
  // }
}
