import { Controller } from '@hotwired/stimulus';

let currentPosition = {coords: {latitude: 51.9247772, longitude: 4.4780972}}
let positionWatchId = null
let incidentlist = null
self = null
const positionWatchOptions = {
    enableHighAccuracy: true,
    timeout: 5000,
    maximumAge: 0,
};

export default class extends Controller {
    static outlets = [ "taken" ]

    initialize() {
        this.element[this.identifier] = this
        self = this
        navigator.geolocation.getCurrentPosition(this.getCurrentPositionSuccess, this.positionWatchError);
        positionWatchId = navigator.geolocation.watchPosition(this.positionWatchSuccess, this.positionWatchError, positionWatchOptions);
        window.addEventListener("childControllerConnectedEvent", function(e){
            if (e.detail.controller.identifier == "incidentlist"){
                incidentlist = e.detail.controller
                incidentlist.positionWatchSuccess(currentPosition)
            }
        });
    }
    connect() {}
    takenOutletConnected(outlet, element){
        console.log("takenListOutletConnected")
        console.log(self.takenListOutlet)
    }
    getCurrentPositionSuccess(position){
        self.positionWatchSuccess(position)
    }
    positionWatchSuccess(position){
        currentPosition = position
        if (incidentlist) {
            incidentlist.positionWatchSuccess(position)
        }
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
        self.getCurrentPositionSuccess(currentPosition)
    }
    showFilters() {
        document.body.classList.add('show-filters')
    }

    hideFilters() {

        document.body.classList.remove('show-filters')
    }
}
