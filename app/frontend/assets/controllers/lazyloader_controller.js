import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        if (entry.target.dataset.src) {
          entry.target.src = entry.target.dataset.src
          delete entry.target.dataset.src
        }
      }
    })
    observer.observe(this.element)
  }
}
