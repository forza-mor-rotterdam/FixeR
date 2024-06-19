import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['externalText', 'internalText', 'newTask', 'form', 'submitContainer']

  connect() {
    this.requiredLabelInternalText = 'Waarom kan de taak niet worden afgerond?'
    this.defaultLabelInternalText = 'Interne opmerking'
    this.defaultErrorMessage = 'Vul a.u.b. dit veld in.'
    const btn = this.element.querySelector('[type="radio"][value="niet_opgelost"]')
    if (btn.checked) {
      this.onResolutionFalse()
    } else {
      this.onResolutionTrue()
    }
    this.formTarget.addEventListener(`submit`, this.handleSubmit.bind(this))
  }

  onResolutionFalse() {
    if (this.hasInternalTextTarget) {
      this.internalTextTarget.querySelector('label').textContent = this.requiredLabelInternalText
      this.internalTextTarget.querySelector('textarea').classList.add('required')
      this.internalTextTarget.closest('.wrapper--flex-order').style.flexDirection = 'column-reverse'
    }
  }

  onResolutionTrue() {
    if (this.hasInternalTextTarget) {
      this.internalTextTarget.querySelector('label').textContent = this.defaultLabelInternalText
      this.internalTextTarget.querySelector('textarea').classList.remove('required')
      this.internalTextTarget.closest('.wrapper--flex-order').style.flexDirection = 'column'
    }
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
    request.timeout = 300000
    request.send(formData)
  }
  onSubmit(event) {
    const allFieldsValid = this.checkValids()
    event.preventDefault()
    if (allFieldsValid) {
      this.formTarget.requestSubmit()
      document.querySelector('body').style.pointerEvents = 'none'
    }
  }
}
