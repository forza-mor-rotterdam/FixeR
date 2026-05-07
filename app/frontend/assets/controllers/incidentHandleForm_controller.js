import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = [
    'externalText',
    'internalText',
    'newTask',
    'form',
    'submitContainer',
    'charCounter',
    'andersNamelijkCharCounter',
    'confirmPopup',
    'redenAfwijzing',
    'reasonHelptext',
    'andersNamelijk',
  ]

  connect() {
    this.confirmedNewTaskSubmission = false
    this.shouldShowReasonHelptext = false
    this.requiredLabelInternalText = 'Opmerking voor mid-office'
    this.defaultLabelInternalText = 'Opmerking voor mid-office'
    this.defaultErrorMessage = 'Vul a.u.b. dit veld in.'
    const btn = this.element.querySelector('[type="radio"][value="niet_opgelost"]')
    if (btn.checked) {
      this.onResolutionFalse()
      const andersBtn = this.element.querySelector('[type="radio"][value="anders"]')
      if (andersBtn && andersBtn.checked && this.hasAndersNamelijkTarget) {
        this.onChangeRedenAfwijzing({ target: andersBtn })
      }
    } else {
      this.onResolutionTrue()
    }

    if (this.hasInternalTextTarget) {
      this.internalTextArea = this.internalTextTarget.querySelector('textarea')
      if (this.internalTextArea) {
        this.internalTextArea.addEventListener('input', this.updateCharacterCounter.bind(this))
        this.updateCharacterCounter()
      }
    }

    if (this.hasAndersNamelijkTarget) {
      this.andersNamelijkTextArea = this.andersNamelijkTarget.querySelector('textarea')
      if (this.andersNamelijkTextArea) {
        this.andersNamelijkTextArea.addEventListener('input', this.updateAndersNamelijkCounter.bind(this))
        this.updateAndersNamelijkCounter()
      }
    }

    if (this.hasRedenAfwijzingTarget) {
      this.redenAfwijzingTarget.addEventListener('change', (event) => {
        if (event.target?.matches('input[type="radio"]')) {
          this.onChangeRedenAfwijzing(event)
        } else {
          this.updateReasonHelptextVisibility()
        }
      })
      this.updateReasonHelptextVisibility()
    }

    this.formTarget.addEventListener(`submit`, this.handleSubmit.bind(this))
  }

  hasSelectedNewTasks() {
    if (!this.hasNewTaskTarget) {
      return false
    }

    return this.newTaskTarget.querySelectorAll('input[type="checkbox"]:checked').length > 0
  }

  openConfirmPopup() {
    if (this.hasConfirmPopupTarget) {
      this.confirmPopupTarget.showModal()
    }
  }

  closeConfirmPopup() {
    if (this.hasConfirmPopupTarget) {
      this.confirmPopupTarget.close()
    }
  }

  confirmCreateTaskAndSubmit() {
    this.confirmedNewTaskSubmission = true
    this.closeConfirmPopup()
    this.formTarget.requestSubmit()
    document.querySelector('body').style.pointerEvents = 'none'
  }

  updateCharacterCounter() {
    if (!this.hasCharCounterTarget || !this.internalTextArea) {
      return
    }

    const currentLength = this.internalTextArea.value.length
    const maxLength = parseInt(this.internalTextArea.getAttribute('maxlength') || '200', 10)
    this.charCounterTarget.textContent = `${currentLength}/${maxLength}`
  }

  updateAndersNamelijkCounter() {
    if (!this.hasAndersNamelijkCharCounterTarget || !this.andersNamelijkTextArea) {
      return
    }

    const currentLength = this.andersNamelijkTextArea.value.length
    const maxLength = parseInt(this.andersNamelijkTextArea.getAttribute('maxlength') || '1000', 10)
    this.andersNamelijkCharCounterTarget.textContent = `${currentLength}/${maxLength}`
  }

  onResolutionFalse() {
    if (this.hasInternalTextTarget) {
      this.internalTextTarget.querySelector('label').textContent = this.requiredLabelInternalText
    }
    if (this.hasRedenAfwijzingTarget) {
      this.redenAfwijzingTarget.hidden = false
      this.shouldShowReasonHelptext = false
      this.updateReasonHelptextVisibility()
    }
  }

  onResolutionTrue() {
    if (this.hasInternalTextTarget) {
      this.internalTextTarget.querySelector('label').textContent = this.defaultLabelInternalText
      this.internalTextTarget.querySelector('textarea').classList.remove('required')
    }
    if (this.hasRedenAfwijzingTarget) {
      this.redenAfwijzingTarget.hidden = true
    }
    if (this.hasReasonHelptextTarget) {
      this.shouldShowReasonHelptext = false
      this.reasonHelptextTarget.hidden = true
    }
    if (this.hasAndersNamelijkTarget) {
      this.andersNamelijkTarget.hidden = true
      const andersNamelijkTextarea = this.andersNamelijkTarget.querySelector('textarea')
      if (andersNamelijkTextarea) {
        andersNamelijkTextarea.classList.remove('required')
      }
    }
  }

  onChangeRedenAfwijzing(event) {
    this.updateReasonHelptextVisibility()
    if (this.hasReasonHelptextTarget) {
      this.shouldShowReasonHelptext = false
      this.reasonHelptextTarget.hidden = true
    }
    this.clearRedenAfwijzingErrors()
    this.clearReasonMessageNodes()

    if (this.hasAndersNamelijkTarget) {
      const isAnders = event.target.value === 'anders'
      this.andersNamelijkTarget.hidden = !isAnders
      const andersNamelijkTextarea = this.andersNamelijkTarget.querySelector('textarea')
      if (andersNamelijkTextarea) {
        andersNamelijkTextarea.classList.toggle('required', isAnders)
      }
    }
  }

  clearRedenAfwijzingErrors() {
    if (!this.hasRedenAfwijzingTarget) {
      return
    }

    this.redenAfwijzingTarget.querySelectorAll('.invalid-text').forEach((errorElement) => {
      errorElement.textContent = ''
    })
    this.redenAfwijzingTarget.querySelectorAll('.form-row').forEach((rowElement) => {
      rowElement.classList.remove('is-invalid')
    })

    // Remove server-rendered field errors for this specific reason message.
    this.formTarget.querySelectorAll('.errorlist li').forEach((listItem) => {
      const normalizedText = (listItem.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase()
      if (normalizedText.includes('maak een keuze uit een van de bovenstaande opties')) {
        listItem.remove()
      }
    })
    this.formTarget.querySelectorAll('.errorlist').forEach((errorList) => {
      if (!errorList.children.length) {
        errorList.remove()
      }
    })
  }

  clearReasonMessageNodes() {
    const reasonMessage = 'maak een keuze uit een van de bovenstaande opties'
    this.element
      .querySelectorAll('.help-block, .invalid-text, .errorlist li, .messages li')
      .forEach((node) => {
        const normalizedText = (node.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase()
        if (normalizedText === reasonMessage) {
          node.remove()
        }
      })
  }

  updateReasonHelptextVisibility() {
    if (!this.hasReasonHelptextTarget || !this.hasRedenAfwijzingTarget) {
      return
    }

    if (this.redenAfwijzingTarget.hidden) {
      this.reasonHelptextTarget.hidden = true
      return
    }

    const selectedReason = this.redenAfwijzingTarget.querySelector('input[type="radio"]:checked')
    this.reasonHelptextTarget.hidden = !!selectedReason || !this.shouldShowReasonHelptext
    this.reasonHelptextTarget.style.display = this.reasonHelptextTarget.hidden ? 'none' : ''
  }

  onChangeResolution(event) {
    if (event.target.value === 'niet_opgelost') {
      this.onResolutionFalse()
    } else {
      this.onResolutionTrue()
    }
  }

  checkValids() {
    const inputList = document.querySelectorAll('textarea')
    let count = 0
    for (const input of inputList) {
      let error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]
      let invalid = input.value.length == 0 && input.classList.contains('required')
      error.textContent = invalid ? this.defaultErrorMessage : ''
      input.closest('.form-row').classList[invalid ? 'add' : 'remove']('is-invalid')
      if (invalid) {
        count++
      }
    }

    const resolutionNietOpgelost = this.element.querySelector(
      '[type="radio"][value="niet_opgelost"]:checked'
    )
    if (resolutionNietOpgelost && this.hasRedenAfwijzingTarget) {
      const selectedReason = this.redenAfwijzingTarget.querySelector(
        'input[type="radio"][name="reden_afwijzing"]:checked'
      )
      const invalidReason = !selectedReason

      this.shouldShowReasonHelptext = invalidReason
      this.updateReasonHelptextVisibility()
      if (invalidReason) {
        count++
      }
    }

    return count === 0
  }
  handleSubmit(event) {
    const self = this
    event.preventDefault()
    const form = event.target
    const formData = new FormData(form)
    var request = new XMLHttpRequest()
    let uploadStart = Date.now()

    self.submitContainerTarget.classList.add('busy')
    document.activeElement.blur()
    let progressContainer = document.createElement('div')
    let progressRemainingTime = document.createElement('div')
    let progressPercentage = document.createElement('div')
    progressContainer.classList.add('container__progress')
    progressRemainingTime.classList.add('progress--time')
    progressPercentage.classList.add('progress--bar')

    self.submitContainerTarget.insertBefore(
      progressContainer,
      self.submitContainerTarget.querySelector('.btn-action')
    )
    progressContainer.insertBefore(progressRemainingTime, null)
    progressContainer.insertBefore(progressPercentage, null)

    request.upload.addEventListener('progress', function (e) {
      if (e.lengthComputable) {
        let duration = Date.now() - uploadStart
        let estimatedRemainingTotalSeconds = (duration * (e.total / e.loaded) - duration) / 1000
        let estimatedRemainingSeconds = Math.round(estimatedRemainingTotalSeconds % 60)
        let estimatedRemainingMinutes =
          (estimatedRemainingTotalSeconds - (estimatedRemainingTotalSeconds % 60)) / 60
        let percentageLoaded = Math.round((e.loaded / e.total) * 100)

        progressRemainingTime.textContent =
          percentageLoaded < 100
            ? `Momentje, de foto('s) worden verzonden. Verwachte resterende tijd: ${estimatedRemainingMinutes}:${String(
                estimatedRemainingSeconds
              ).padStart(2, '0')}`
            : 'De upload is geslaagd. Je gaat nu terug naar het taken overzicht.'
        progressPercentage.style.width = `${percentageLoaded}%`
      }
    })
    request.onreadystatechange = function () {
      if (this.readyState == 4 && this.status == 200) {
        window.location.replace('/taken/')
      }
    }

    request.open('post', form.action)
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
    request.timeout = 300000
    request.send(formData)
  }
  onSubmit(event) {
    const allFieldsValid = this.checkValids()
    event.preventDefault()
    if (!allFieldsValid) {
      return
    }

    if (this.hasSelectedNewTasks() && !this.confirmedNewTaskSubmission) {
      this.openConfirmPopup()
      return
    }

    this.confirmedNewTaskSubmission = false
    if (allFieldsValid) {
      this.formTarget.requestSubmit()
      document.querySelector('body').style.pointerEvents = 'none'
    }
  }
}
