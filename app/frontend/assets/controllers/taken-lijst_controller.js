import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static showSortingContainer = false
  static showSearchContainer = false
  static sortDirectionReversed = false

  currentPosition = null
  distanceThreshold = 50 // meter
  page = sessionStorage.getItem('page_number') || 1
  lastRefreshPosition = null

  static outlets = ['taken-kaart']
  static targets = ['taakItem', 'containerHeader']

  selecteerTaakItem(taakUuid, preventScroll) {
    const taakItemTarget = this.taakItemTargets.find((elem) => elem.dataset.uuid === taakUuid)
    taakItemTarget?.classList.toggle('highlight-once', taakItemTarget.dataset.uuid === taakUuid)
    preventScroll || taakItemTarget?.scrollIntoView()
    setTimeout(() => {
      taakItemTarget?.classList.remove('highlight-once')
    }, 2000)
  }
  deselecteerTaakItem(taakUuid) {
    const taakItemTarget = this.taakItemTargets.find((elem) => elem.dataset.uuid === taakUuid)
    taakItemTarget?.classList.remove('active')
  }
  selectTaakMarker(e) {
    if (this.hasTakenKaartOutlet) {
      const preventScroll = e.params['preventScroll'] != false
      this.takenKaartOutlet.selectTaakMarker(e.params.taakUuid, preventScroll)
    }
  }
  getKaartMarkers() {
    return this.taakItemTargets
      .filter((taakItem) => {
        try {
          JSON.parse(taakItem.dataset.geometrie)
          return true
        } catch (err) {
          return false
        }
      })
      .map((taakItem) => {
        return {
          geometrie: JSON.parse(taakItem.dataset.geometrie),
          adres: taakItem.dataset.adres,
          afbeeldingUrl: taakItem.dataset.afbeeldingUrl,
          taakUuid: taakItem.dataset.uuid,
          titel: taakItem.dataset.titel,
          hasRemark: taakItem.dataset.hasRemark,
        }
      })
  }
}
