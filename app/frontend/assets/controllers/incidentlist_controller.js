import { Controller } from '@hotwired/stimulus';

let showSortingContainer = false;
let sortDirectionReversed = false;
let mapHasBeenLoaded = false
let markers = null
export default class extends Controller {

    static values = {
        kaart: Object,
    }
    static targets = [ "sorting" ]

    initialize() {
        
    }

    connect(e) {
        if(this.hasSortingTarget && showSortingContainer === true ) {
            this.sortingTarget.classList.remove("hidden-vertical")
            this.sortingTarget.classList.add("show-vertical")
        }
    }

    toggleMapView(e) {
        console.log('kllik', document.getElementById('taken_lijst'))
        document.getElementById('taken_lijst').classList.toggle('showMap')

        if(!mapHasBeenLoaded){
            mapHasBeenLoaded = true
            const coordinatenlijst = this.kaartValue.kaart_taken_lijst

            console.log('coordinatenlijst', coordinatenlijst)
                        
            const map = L.map('incidentMap')
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                minZoom: 13,
                maxZoom: 18,
                attribution: ''
            }).addTo(map);

            //create the marker group
            markers = new L.featureGroup();
            this.plotMarkers(coordinatenlijst);
            //add the markers to the map
            map.addLayer(markers);
            //fit the map to the markers
            map.fitBounds(markers.getBounds());
        }
    }

    plotMarkers(coordinatenlijst) {
        if(coordinatenlijst){
            var len = coordinatenlijst.length;
            for(var i = 0; i<len; i++)
            {
                var lat = coordinatenlijst[i].geometrie.coordinates[1]
                var long = coordinatenlijst[i].geometrie.coordinates[0]
                var marker =  L.marker(new L.LatLng(lat,long))

                const adres = coordinatenlijst[i].adres;
                const afbeelding = coordinatenlijst[i].afbeelding;
                const omschrijving = coordinatenlijst[i].omschrijving;
                const taakId = coordinatenlijst[i].taak_id
                let showImage = false

                if(typeof(afbeelding) === 'string') showImage = true
                    var markerLocation = new L.LatLng(lat, long);
                    var marker = new L.Marker(markerLocation);
                if (showImage) {
                    marker.bindPopup(`<div class="container__image"><img src=${afbeelding}></div><div class="container__content"><a href="/taak/${taakId}" target="_top" aria-label="Bekijk taak ${taakId}">${adres}</a><p>${omschrijving}</p></div>`);
                }else{
                    marker.bindPopup(`<div>${adres}</div>`);
                }

                markers.addLayer(marker);
            }
        }

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

    bekijkTakenOpKaart(e) {
        
    }

    makeRoute(e) {
        console.log("makeRoute, e", e.params)
        console.log("makeRoute, e", e.params.incidents)
        // let routeUrl = "https://www.google.com/maps/dir"

        // function handleCurrentLocation(pos) {
        //     const crd = pos.coords;
        //     routeUrl += `/${crd.latitude}+${crd.longitude}`
        //     getRoute()
        // }

        // function handleNoCurrentLocation(error) {
        //     switch(error.code) {
        //         case error.PERMISSION_DENIED:
        //           console.log("User denied the request for Geolocation.")
        //           break;
        //         case error.POSITION_UNAVAILABLE:
        //           console.log("Location information is unavailable.")
        //           break;
        //         case error.TIMEOUT:
        //           console.log("The request to get user location timed out.")
        //           break;
        //         case error.UNKNOWN_ERROR:
        //           console.log("An unknown error occurred.")
        //           break;
        //       }
        //     getRoute()
        // }

        // function getRoute() {
        //     e.params.incidents.map((incident)=> {
        //         let houseNumber = incident?.locatie?.adres?.huisnummer != undefined ? incident.locatie.adres.huisnummer : ""
        //         const address = `${incident?.locatie?.adres?.straatNaam} ${houseNumber} Rotterdam`
        //         routeUrl += `/${address}`
        //     })
        //     window.open(routeUrl, "_blank")
        // }

        // navigator.geolocation.getCurrentPosition(handleCurrentLocation, handleNoCurrentLocation);
    }
}
