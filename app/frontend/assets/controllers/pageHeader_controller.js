import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['containerUitklapper']

  connect() {
    window.addEventListener('click', (e) => {
      if (
        !(e.target.closest('.container__uitklapper') || e.target.hasAttribute('data-action')) || // data-action conflicts with window.evenlistener
        e.target.classList.contains('btn-close--small')
      ) {
        this.element.querySelectorAll('.container__uitklapper.show').forEach((element) => {
          element.classList.remove('show')
        })
      }
      console.log('toggle show--notificatie-lijst')
      document.body.classList.toggle(
        'show--notificatie-lijst',
        this.element.querySelector('.show .container__profiel_notificatie_lijst')
      )
    })
    this.element.addEventListener('keydown', function (e) {
      if (e.code == 'Space' || e.code == 'Enter') {
        e.preventDefault()
        document.activeElement.click()
      }
    })
  }

  resetFontSize() {
    document.body.classList.remove('fz-medium', 'fz-large', 'fz-xlarge')
  }

  setFontSize(e) {
    const size = e.params.size
    if (size) {
      this.resetFontSize()
      document.body.classList.add(size)
    }
  }

  show(e) {
    if (
      (e.target.tagName.toUpperCase() != 'A' &&
        e.target.tagName.toUpperCase() != 'BUTTON' &&
        !e.target.closest('.content--uitklapper')) ||
      e.target.classList.contains('container__uitklapper')
    ) {
      if (this.element.querySelectorAll('.show').length) {
        this.element.querySelectorAll('.show').forEach((element) => {
          if (element != e.target.closest('.container__uitklapper')) {
            element.classList.remove('show')
          }
          e.target.closest('.container__uitklapper').classList.toggle('show')
        })
      } else {
        e.target.closest('.container__uitklapper').classList.add('show')
      }
    }
    document.body.classList.toggle(
      'show--notificatie-lijst',
      this.element.querySelector('.show .container__profiel_notificatie_lijst')
    )
  }
}
