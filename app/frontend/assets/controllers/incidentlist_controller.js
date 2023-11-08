import { Controller } from '@hotwired/stimulus';

let showSortingContainer = false;
let sortDirectionReversed = false;
let currentPosition = [51.919489, 4.465413]
let positionWatchId = null
self = null
const positionWatchOptions = {
    enableHighAccuracy: false,
    timeout: 5000,
    maximumAge: 0,
};
const orderOptions = [
    "Datum",
    "Adres",
    "Afstand",
    "Postcode",
]
let activeOrder = orderOptions[0]
const url = "https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{layerName}/{crs}/{z}/{x}/{y}.{format}";

export default class extends Controller {
    static outlets = [ "kaart" ]
    static targets = [ "sorting", "toggleMapView", "taakAfstand", "taakItem", "taakItemLijst"]

    initialize() {

    }
    taakAfstandTargetConnected(element) {
        const markerLocation = new L.LatLng(element.dataset.latitude, element.dataset.longitude);
        element.textContent = Math.round(markerLocation.distanceTo(currentPosition))
    }
    connect(e) {
        this.element[this.identifier] = this
        self = this
        positionWatchId = navigator.geolocation.watchPosition(this.positionWatchSuccess, this.positionWatchError, positionWatchOptions);

        if(this.hasSortingTarget && showSortingContainer === true ) {
            this.sortingTarget.classList.remove("hidden-vertical")
            this.sortingTarget.classList.add("show-vertical")
        }

        self.setStyleOrder(activeOrder)
        self.taakItemLijstTarget.style.flexDirection = "column"
        let kaartMarkers = []
        for (let i = 0; i < self.taakItemTargets.length; i++){
            const taakItem = self.taakItemTargets[i]
            if (taakItem.dataset.geometrie != ""){
                kaartMarkers.push({
                    geometrie: JSON.parse(taakItem.dataset.geometrie),
                    adres: taakItem.dataset.adres,
                    afbeeldingUrl: taakItem.dataset.afbeeldingUrl,
                    onderwerpen: taakItem.dataset.onderwerpen,
                    taakId: taakItem.dataset.id,
                })
            }
        }
        this.kaartOutlet.plotMarkers(kaartMarkers)
    }
    positionWatchSuccess(position){
        currentPosition = [position.coords.latitude, position.coords.longitude]
        self.kaartOutlet.positionChangeEvent(position)
        self.taakItemLijstTarget.style.display = "flex"
        for(let i = 0; i < self.taakAfstandTargets.length; i++){
            const elem = self.taakAfstandTargets[i]
            const markerLocation = new L.LatLng(elem.dataset.latitude, elem.dataset.longitude);
            const afstand = Math.round(markerLocation.distanceTo(currentPosition))
            elem.textContent = afstand
            const listItem = elem.closest(".list-item")

            if (listItem){
                listItem.dataset.orderAfstand = afstand
                if (activeOrder == "Afstand"){
                    listItem.style.order = parseInt(afstand)
                }
            }
        }
    }
    setStyleOrder(order){
        for(let i = 0; i < self.taakItemTargets.length; i++){
            const taakItem = self.taakItemTargets[i]
            taakItem.style.order = taakItem.dataset[`order${order}`]
        }
    }
    sorterenOp(e){
        let selectedOrder = e.target.value.split("-")[0]
        if (selectedOrder != activeOrder){
            self.setStyleOrder(selectedOrder)
        }
        activeOrder = selectedOrder
        self.taakItemLijstTarget.style.flexDirection = e.target.value.replace(e.target.value.split("-")[0], "column")
    }
    positionWatchError(error){
        console.log("handleNoCurrentLocation, error: ", error)
        switch(error.code) {
            case error.PERMISSION_DENIED:
              console.log("User denied the request for Geolocation.")
              break;
            case error.POSITION_UNAVAILABLE:
              console.log("Location information is unavailable.")
              break;
            case error.TIMEOUT:
              console.log("The request to get user location timed out.")
              break;
            case error.UNKNOWN_ERROR:
              console.log("An unknown error occurred.")
              break;
        }
        self.positionWatchSuccess({
            coords: {
                latitude: currentPosition[0],
                longitude: currentPosition[1],
            }
        })
    }
    disconnect() {
        console.log("disconnect")
    }

    toggleMapView(e) {
        document.getElementById('taken_lijst').classList.toggle('showMap')
    }
    onGroup(e) {
        console.log("onGroup", e.target.checked)
        const frame = document.getElementById('incidents_list');
        const url = `${frame.dataset.src}?grouped-by=${e.target.checked}`
        frame.setAttribute('src', url);
    }

    onToggleSortingContainer() {
        this.sortingTarget.classList.toggle("hidden-vertical")
        this.sortingTarget.classList.toggle("show-vertical")
        showSortingContainer = !showSortingContainer
        sortDirectionReversed = sortDirectionReversed === undefined ? false : true
    }

    onSort(e) {
        const frame = document.getElementById('incidents_list');
        const url = `${frame.dataset.src}?sort-by=${e.target.value}`
        frame.setAttribute('src', url);
    }
}
