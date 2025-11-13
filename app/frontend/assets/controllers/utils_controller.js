import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['dateVerbose']
  static values = {
    date: String,
  }

  dateVerboseTargetConnected(element) {
    const dateString = element.dataset.utilsDateValue
    const label = this.formatDateLabel(dateString)
    element.textContent = label
  }

  goToUrl(e) {
    window.location.href = e.params.url
  }

  foldOut() {
    this.element.classList.toggle('show')
  }

  formatDateLabel(dateString) {
    if (!dateString) return ''

    const inputDate = this.parseDutchDate(dateString)
    if (!inputDate || isNaN(inputDate)) return dateString

    const now = new Date()
    const inputDay = new Date(inputDate.getFullYear(), inputDate.getMonth(), inputDate.getDate())
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())

    const diffDays = Math.round((today - inputDay) / (1000 * 60 * 60 * 24))

    if (diffDays === 0) return 'Vandaag'
    if (diffDays === 1) return 'Gisteren'
    if (diffDays === 2) return 'Eergisteren'

    const formatted = new Intl.DateTimeFormat('nl-NL', {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    }).format(inputDate)

    let result = formatted.replace(/\b([A-Z][a-z]{2})\b/g, (maand) => maand.toLowerCase())
    const currentYear = now.getFullYear()
    result = result.replace(new RegExp(`\\s*${currentYear}\\b`, 'g'), '').trim()

    return result.charAt(0).toUpperCase() + result.slice(1)
  }

  parseDutchDate(str) {
    const months = {
      jan: 0,
      januari: 0,
      feb: 1,
      februari: 1,
      mrt: 2,
      maart: 2,
      apr: 3,
      april: 3,
      mei: 4,
      jun: 5,
      juni: 5,
      jul: 6,
      juli: 6,
      aug: 7,
      augustus: 7,
      sep: 8,
      sept: 8,
      september: 8,
      okt: 9,
      oktober: 9,
      nov: 10,
      november: 10,
      dec: 11,
      december: 11,
    }

    const match = str.match(/(\d{1,2})\s+([a-zé]+)\s+(\d{4})/)
    if (!match) return null

    const [, day, monthName, year] = match
    const month = months[monthName]
    if (month === undefined) return null

    return new Date(year, month, day)
  }
}
