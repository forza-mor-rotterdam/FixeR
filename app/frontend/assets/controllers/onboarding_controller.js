import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static values = {
    dateObject: String,
  }

  //   static targets = ['']

  connect() {
    console.log('connecting onboarding controller')
  }
}
