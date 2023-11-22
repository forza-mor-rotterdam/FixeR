import { Controller } from '@hotwired/stimulus';

let showSortingContainer = false;
let sortDirectionReversed = false;
let currentPosition = null
self = null
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
        this.element[this.identifier] = this
        self = this
        this.element.addEventListener("orderChangeEvent", function(e){
            self.sorterenOp(e.detail.order)
            self.saveSortedList(e.detail.order)
        });

        if(this.hasSortingTarget && showSortingContainer === true ) {
            this.sortingTarget.classList.remove("hidden-vertical")
            this.sortingTarget.classList.add("show-vertical")
        }
        self.setStyleOrder(activeOrder)
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

        this.element.addEventListener("markerSelectedEvent", function(e){
            self.selecteerTaakItem(e.detail.taakId)
        });
        this.element.addEventListener("markerDeselectedEvent", function(e){
            self.deselecteerTaakItem(e.detail.taakId)
        });
        window.addEventListener("positionChangeEvent", function(e){
            console.log("positionChangeEvent")
            console.log(e.detail)
            self.positionWatchSuccess(e.detail.position)
        });
        self.element.addEventListener("kaartModusChangeEvent", function(e){
            self.kaartOutlet.kaartModusChangeHandler(e.detail.kaartModus, e.detail.requestType)
        });
        let childControllerConnectedEvent = new CustomEvent('childControllerConnectedEvent', { bubbles: true, cancelable: false, detail: {
            controller: self
        }});

        window.dispatchEvent(childControllerConnectedEvent);
    }
    connect() {}
    taakAfstandTargetConnected(element) {
        const markerLocation = new L.LatLng(element.dataset.latitude, element.dataset.longitude);
        element.textContent = Math.round(markerLocation.distanceTo(currentPosition))
    }
    selecteerTaakItem(taakId) {
        for(let i =0; i < self.taakItemTargets.length; i++){
            if (self.taakItemTargets[i].dataset.id == taakId){
                self.taakItemTargets[i].classList.add("selected")
                self.taakItemTargets[i].scrollIntoView({ behavior: "smooth", block: "end", inline: "nearest" })
            } else {
                self.taakItemTargets[i].classList.remove("selected")
            }
        }
    }
    deselecteerTaakItem(taakId){
        for(let i =0; i < self.taakItemTargets.length; i++){
            self.taakItemTargets[i].classList.remove("selected")
        }
    }
    positionWatchSuccess(position){
        console.log("positionWatchSuccess")
        currentPosition = [position.coords.latitude, position.coords.longitude]
        if (self.hasKaartOutlet){
            self.kaartOutlet.positionChangeEvent(position)
        }
        if (self.hasTaakAfstandTarget){
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
    }
    selectTaakMarker(e) {
        self.kaartOutlet.selectTaakMarker(e.params.taakId)
    }
    setStyleOrder(order){
        for(let i = 0; i < self.taakItemTargets.length; i++){
            const taakItem = self.taakItemTargets[i]
            taakItem.style.order = taakItem.dataset[`order${order}`]
        }
    }
    sorterenOp(order){
        console.log('order', order)
        let selectedOrder = order.split("-")[0]
        if (selectedOrder != activeOrder){
            self.setStyleOrder(selectedOrder)
        }
        activeOrder = selectedOrder
        self.taakItemLijstTarget.classList[(order.split("-").length > 1) ? "remove" : "add"]("reverse")
        self.taakItemLijstTarget.scrollTop = 0;
    }

    saveSortedList(order) {
        let initialSortedList = Array.from(document.querySelectorAll(".list-item"))

        let newSortedList = initialSortedList.map((taakItem) => {
            return Number(taakItem.getAttribute('data-id'))
        })

        if(order.split("-").length > 1){
            newSortedList.reverse()
        }
        sessionStorage.setItem("taakIdList", newSortedList)
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
