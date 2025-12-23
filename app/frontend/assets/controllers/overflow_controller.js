import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {
    const wrapper = this.element.querySelector('.container__overflow').closest('.wrapper')
    const container = this.element.querySelector('.container__overflow')
    const content = this.element.querySelector('.content__overflow')

    if (content.scrollHeight > container.clientHeight) {
      console.log(12345, this.element)
      console.log(12345, this.element.closest('.alert'))
      this.element.closest('.alert').classList.add('has-overflow')
      const label = document.createElement('span')
      label.classList.add('toggle')
      label.textContent = 'Lees meer'

      this.element.insertBefore(label, container.nextElementSibling)

      this.element.addEventListener('click', function () {
        wrapper.classList.toggle('show')
        if (label.textContent == 'Lees meer') {
          label.textContent = 'Lees minder'
        } else {
          label.textContent = 'Lees meer'
        }
      })
    }
  }
}
