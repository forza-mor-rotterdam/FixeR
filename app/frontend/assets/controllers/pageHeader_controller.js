import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {
    document.addEventListener('keydown', function (e) {
      if (e.code == 'Space' || e.code == 'Enter') {
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
    if (e.target.tagName != 'A') {
      this.element.querySelectorAll('.show').forEach((element) => {
        if (element != e.target.closest('.container__uitklapper')) {
          element.classList.remove('show')
        }
      })
      e.target.closest('.container__uitklapper').classList.toggle('show')
    }
  }
}
