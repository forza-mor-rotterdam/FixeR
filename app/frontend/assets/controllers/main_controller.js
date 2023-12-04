import { Controller } from '@hotwired/stimulus';

let currentPosition = {coords: {latitude: 51.9247772, longitude: 4.4780972}}
let positionWatchId = null
let incidentlist = null

const positionWatchOptions = {
    enableHighAccuracy: true,
    timeout: 5000,
    maximumAge: 0,
};
let kaartModus = null
let kaartStatus = null

export default class extends Controller {
    static outlets = [ "taken" ]
    static values = {
        mercurePublisherJwtKey: String,
        mercureSubscriberJwtKey: String,
    }

    initialize() {
        let self = this
        self.element[self.identifier] = self
        const status = {
            zoom: 16,
            center: [currentPosition.coords.latitude, currentPosition.coords.longitude],
        }
        kaartModus = "volgen"
        kaartStatus = {
            "volgen": status,
            "toon_alles": status,
        }
        if(!sessionStorage.getItem("kaartStatus")){
            sessionStorage.setItem("kaartStatus", JSON.stringify(kaartStatus));
        }

        navigator.geolocation.getCurrentPosition(self.getCurrentPositionSuccess.bind(self), self.positionWatchError.bind(self));
        positionWatchId = navigator.geolocation.watchPosition(self.positionWatchSuccess.bind(self), self.positionWatchError.bind(self), positionWatchOptions);
        window.addEventListener("childControllerConnectedEvent", function(e){
            if (e.detail.controller.identifier == "incidentlist"){
                incidentlist = e.detail.controller
                incidentlist.positionWatchSuccess(currentPosition)
            }
        });

        // The subscriber subscribes to updates for the https://example.com/users/dunglas topic
        // and to any topic matching https://example.com/books/{id}
        const url = new URL('http://localhost:7001/.well-known/mercure?topic=mytopicname');
        // url.searchParams.append('topic', 'https://example.com/books/{id}');
        // url.searchParams.append('topic', 'mytopicname');
        // The URL class is a convenient way to generate URLs such as https://localhost/.well-known/mercure?topic=https://example.com/books/{id}&topic=https://example.com/users/dunglas

        console.log(self.mercureSubscriberJwtKeyValue)
        let token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJtZXJjdXJlIjp7InN1YnNjcmliZSI6WyJteXRvcGljbmFtZSJdLCJwdWJsaXNoIjpbIm15dG9waWNuYW1lIl19fQ.k0kjyeyOP2Sw9YC8KbaMgumX1jxptAh7dLoznpSpymY"
        const eventSource = new EventSource(url
            // , {
            //     // withCredentials: true,
            //     headers: {
            //         Authorization: 'Bearer ' + token
            //     }
            // }
        );

        // The callback will be called every time an update is published
        eventSource.onmessage = e => console.log(e); // do something with the payload
        eventSource.onerror = (e) => {
            console.log(e)
            console.log("An error occurred while attempting to connect.");
            eventSource.close()
          };

    }
    connect() {}
    takenOutletConnected(outlet, element){
        let self = this
        console.log("takenListOutletConnected")
        console.log(self.takenListOutlet)
    }
    getCurrentPositionSuccess(position){
        let self = this
        console.log("getCurrentPositionSuccess controller id:", self.identifier)
        self.positionWatchSuccess(position)
    }
    positionWatchSuccess(position){
        let self = this
        currentPosition = position
        console.log("positionWatchSuccess controller id:", self.identifier)
        if (incidentlist) {
            incidentlist.positionWatchSuccess(position)
        }
    }
    positionWatchError(error){
        let self = this
        console.log("positionWatchError controller id:", self.identifier)
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
    setKaartModus(_kaartModus){
        kaartModus = _kaartModus
    }
    getCurrentPosition(){
        return currentPosition
    }
    getKaartModus(){
        return kaartModus
    }
    setKaartStatus(_kaartStatus){
        kaartStatus[kaartModus] = _kaartStatus
        let sessionState = JSON.parse(sessionStorage.getItem("kaartStatus"))
        sessionState[kaartModus] = _kaartStatus
        const sessionStateString = JSON.stringify(sessionState)
        sessionStorage.setItem("kaartStatus", sessionStateString);
    }
    getKaartStatus(){
        const sessionState = JSON.parse(sessionStorage.getItem("kaartStatus"))
        return sessionState[kaartModus];
    }
}
