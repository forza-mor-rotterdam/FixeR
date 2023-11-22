import { Controller } from '@hotwired/stimulus';

let markers = null
let markerList = []
let markerIcon, markerBlue, markerGreen, markerMagenta = null
let markerMe = null
let mapDiv = null
let map = null
let self = null
let zoomLevel = 16
const url = "https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{layerName}/{crs}/{z}/{x}/{y}.{format}";
let buurten = null;
let kaartStatus = null

export default class extends Controller {
    static outlets = [ "main" ]
    initialize() {
        markerMe = null
        kaartStatus = {}
        markerList = []
        self = this
        self.element[self.identifier] = self

        mapDiv = document.getElementById('incidentMap')
        map = L.map('incidentMap', self.mainOutlet.getKaartStatus())
        if(mapDiv){
            this.drawMap()
        }

        map.on('moveend', () => {
            self.mainOutlet.setKaartStatus(
                {
                    zoom: map.getZoom(),
                    center: map.getCenter(),
                }
            )
        })
        map.on('zoomend', () => {
            self.mainOutlet.setKaartStatus(
                {
                    zoom: map.getZoom(),
                    center: map.getCenter(),
                }
            )
        })
        map.on('popupopen', ({ popup }) => {
            if (popup instanceof L.Popup) {
                const marker = popup._source;
                let markerSelectedEvent = new CustomEvent('markerSelectedEvent', { bubbles: true, cancelable: false, detail: {taakId:marker.options.taakId}});
                self.element.dispatchEvent(markerSelectedEvent);
            }
        });
        map.on('popupclose', ({ popup }) => {
            if (popup instanceof L.Popup) {
                const marker = popup._source;
                let markerSelectedEvent = new CustomEvent('markerDeselectedEvent', { bubbles: true, cancelable: false, detail: {taakId:marker.options.taakId}});
                self.element.dispatchEvent(markerSelectedEvent);

            }
        });
    }
    kaartModusChangeHandler(_kaartModus, _requestType){
        console.log("kaartModusChangeHandler")
        if (!markerMe){
            return
        }
        self.mainOutlet.setKaartModus(_kaartModus)
        switch(_kaartModus){
            case "volgen":
                map.flyTo(markerMe.getLatLng(), self.mainOutlet.getKaartStatus().zoom)
                break;

            case "toon_alles":
                map.fitBounds(markers.getBounds());
                break;

        }
    }
    positionChangeEvent(position){
        if(!markerMe) {
            markerMe = new L.Marker([position.coords.latitude, position.coords.longitude], {icon: markerBlue});
            markers.addLayer(markerMe)
        }else{
            markerMe.setLatLng([position.coords.latitude, position.coords.longitude]);
        }
        if (self.mainOutlet.getKaartModus() == "volgen"){
            map.setView(
                markerMe.getLatLng(),
                self.mainOutlet.getKaartStatus().zoom
            )
        }
    }

    disconnect() {}

    selectTaakMarker(taakId) {
        let obj = markerList.find(obj => obj.options.taakId == taakId);
        obj.openPopup()
    }

    drawMap() {
        markerIcon = L.Icon.extend({
            options: {
                iconSize:     [36, 36],
                iconAnchor:   [18, 30],
                popupAnchor:  [0, -7]
            }
        });

        markerGreen = new markerIcon({iconSize: [36, 36], iconAnchor: [18, 20], iconUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgZmlsdGVyPSJ1cmwoI2ZpbHRlcjBfZF80MzIwXzM3ODEwKSI+CjxwYXRoIGZpbGwtcnVsZT0iZXZlbm9kZCIgY2xpcC1ydWxlPSJldmVub2RkIiBkPSJNMjcuNzc4NSA2LjIyMTY4QzIzLjUwMDUgMS45NDM2OCAxNi41MDAyIDEuOTQzNjggMTIuMjIyMiA2LjIyMTY4QzcuOTQ0MTcgMTAuNDk5NyA3Ljk0NDE3IDE3LjUgMTIuMjIyMiAyMS43NzhMMjAuMDAwMyAyOS41NTYyTDI3Ljc3ODUgMjEuNzc4QzMyLjA1NjUgMTcuNSAzMi4wNTY1IDEwLjQ5OTcgMjcuNzc4NSA2LjIyMTY4Wk0yMC4wMDAzIDE3Ljk5OTlDMjIuMjA5NSAxNy45OTk5IDI0LjAwMDMgMTYuMjA5IDI0LjAwMDMgMTMuOTk5OUMyNC4wMDAzIDExLjc5MDcgMjIuMjA5NSA5Ljk5OTg2IDIwLjAwMDMgOS45OTk4NkMxNy43OTEyIDkuOTk5ODYgMTYuMDAwMyAxMS43OTA3IDE2LjAwMDMgMTMuOTk5OUMxNi4wMDAzIDE2LjIwOSAxNy43OTEyIDE3Ljk5OTkgMjAuMDAwMyAxNy45OTk5WiIgZmlsbD0iIzAwODExRiIvPgo8Y2lyY2xlIGN4PSIyMCIgY3k9IjE0IiByPSI0IiBmaWxsPSJ3aGl0ZSIvPgo8L2c+CjxkZWZzPgo8ZmlsdGVyIGlkPSJmaWx0ZXIwX2RfNDMyMF8zNzgxMCIgeD0iMCIgeT0iMCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBmaWx0ZXJVbml0cz0idXNlclNwYWNlT25Vc2UiIGNvbG9yLWludGVycG9sYXRpb24tZmlsdGVycz0ic1JHQiI+CjxmZUZsb29kIGZsb29kLW9wYWNpdHk9IjAiIHJlc3VsdD0iQmFja2dyb3VuZEltYWdlRml4Ii8+CjxmZUNvbG9yTWF0cml4IGluPSJTb3VyY2VBbHBoYSIgdHlwZT0ibWF0cml4IiB2YWx1ZXM9IjAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDEyNyAwIiByZXN1bHQ9ImhhcmRBbHBoYSIvPgo8ZmVPZmZzZXQgZHk9IjQiLz4KPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMiIvPgo8ZmVDb21wb3NpdGUgaW4yPSJoYXJkQWxwaGEiIG9wZXJhdG9yPSJvdXQiLz4KPGZlQ29sb3JNYXRyaXggdHlwZT0ibWF0cml4IiB2YWx1ZXM9IjAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAuMjUgMCIvPgo8ZmVCbGVuZCBtb2RlPSJub3JtYWwiIGluMj0iQmFja2dyb3VuZEltYWdlRml4IiByZXN1bHQ9ImVmZmVjdDFfZHJvcFNoYWRvd180MzIwXzM3ODEwIi8+CjxmZUJsZW5kIG1vZGU9Im5vcm1hbCIgaW49IlNvdXJjZUdyYXBoaWMiIGluMj0iZWZmZWN0MV9kcm9wU2hhZG93XzQzMjBfMzc4MTAiIHJlc3VsdD0ic2hhcGUiLz4KPC9maWx0ZXI+CjwvZGVmcz4KPC9zdmc+Cg=='})
        markerBlue = new markerIcon({iconSize: [26, 26], iconAnchor: [13, 13], iconUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAATESURBVHgBrVZNTGNVFL7vp9AfCB0mpAOSoRgdGUQcI8yiCYImGjXExBBYGbshcdGiKxHHhSVRdG+M0YWrccUC4qSz0EQT2RATiNHEBFKcjnYmg6BtLfa/7/qdx72vr50OU+qc5OTed9895zvn3HPOvYw1SZxzL/gt8Br4Bq8Szb8HB8F+9qAolUqdgcIIOMmbowj7vwQlg3XeNUu/5XK5wZN0Kw3AFBCDoN/pdH6HJb/8t3GTsWu7nEV3GbuZOl4b9TH2BPjKhMIGvDWqboCfA8dJ34nAApRjqmK+J0FTecY+2uDs0x/ZiRS6fGxAl7MKnkgkxvr7+5NCr0VqjRX4GYlE1Eql8r4d9KWr9wcloj0vY286by0N9vX1vWl6A6dqsOpkFSTTw11dXTG58M63zYHaKQzPP37eUp3c2tq6MDY29hfmltdqnRGqw+F4Vi7QOZ4WlIhkKB8EeUdGRoICS7kncFtb2+tyYWWDs1aIpKK7lqyiadpkQ2ARf2JdVdUB+fOXO6xlurZTnUPnaG9vr+Mu4OXlZWV4eFjr7u52YNN5+fPnP1nL9Hu6Bvh8qVTSCENiKjYD2sAueP+3FOj4sLVQS8WZ9ywHqU7P+v3+3Pj4eGl1dbVios/OziqoNaWzs1ODZQm5e6CLtUzUVCShPP/AoMbjcRWg5poJjA+lUChomUxGQ8f6VQpMX2At06gNGLpvsWpyKcz2wQ4ODszF/f19q4CmH1NYK0RS7z5TDXMsFltj1WO1gPnU1BTr6emhA+VLS0trCE2Gfk4gv0Pj7NQUuqzUHNP6+jo5owDDArfqGJlnAkej0X9g4Vdy/Qosf9LHmiYK8dJE9XtnZ+fzlZWVREdHh0HfcNLEMYEnJycNAWwg+yoLCwtX8/n8bfpHDf/6awoLjze4yhp4Snu94pKgsx0aGvoMo3F0dGTgOI16GTKAtp/BVUh1/Hg4HH4FiXbLfsnGU5y/8bXBA18Y3PPBMQ9/YvC3vzH4D/HaC5lkQ6HQNDrhsMvl6odOL8rJSZeQHZicoTruBJ9rb29/FOOl+fn5V7PZ7G1+SiIZkkXfvwQ9j4B9ON8OgXFX4DS0NTdq+SzmA7D0IsYxcGB7e/tL6DPuB4gekKG9gUDgBYA+DdmLIoLdYBdhSGClLtw6uB3shoDHMAw39FE3cwSDwYdmZmaeQud50ePxnEP4ekkIIb2TTCZje3t7Py0uLl7f3NxMAxQ2lHL4nQX/K8YCuMTE1VgtNlwUc3Nz1Fl0r9frKhaLLoTMTUZAERmjQ5nOqjcayXJd15VyuUxJw7GvjLGMfQSSdbvdWSICRXc0W6X9bOvPmsLhEMnmFCFyQmmbBCcwKQtQGgi4QsAClN4gOTwo8um0+R4hTyvM9hDQ2L3J9AJhNaDMIAKggeZSxrQCNkehlDiP7zyOIIfkzEEmjzIqoG5L6NGGHbSRx5JUVj1zh2DTY5y9jhrXoFyFXtNArBlYq8DIIi79IhKzdHh4SMaUpQPNAtuvS4qKhnKgm0vHm0yzGcbRkTiaAxehLKNWyUOaUxUY9a/LZsl8Dglw8tiJ65PO3CPZ5/N5qAzZcT44RJTU+ldlS0RKhCIz/Dg3XY7IVjMiYrSSrhmPWqFGcqcK6X9czfgLQYqNowAAAABJRU5ErkJggg=='})
        // markerMagenta = new markerIcon({iconUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAATuSURBVHgBrVZNbBtFFJ7ZWdtrO06ciJBaCakbaCuigAqI8iOE03JBSIhc4gMSDQcOHIC2CKRegARxQAiVcEAI6AG1ICFyQAIJCaEWWwUaIlUgqCOkRombuG6l/DjOj72/M31vs95Ybtb5aT5pdnd2Zt733pv35g0lW8Tfh05ENZ9vgFLaC91DhIj42gjNUiGygtKvuSSlnxj9MLsVeXSzCRefOtXs163jQojjQBolm4IOPTb20eCms+oN/nX4rX0w5QJ8xsn2MKUS8Uxi7OMprwlS7Q+wDJWh6Z2TIvYphJ6/9PipOMjbnBhJATiTKjsndcklbl345ck3WxxjvImRdHBwUBp99O337pDUJY9y+Q3bmhryWk3o+Ude72pgygTZJYD7CpNW8cCLl7+cX+uuQa5RQvIxdqSeIH+smXS9mySh/e1EjiikkLpCrg3/RPQbhQ3ng9DoPVJkAD6HofEKuVRLLAv5WD3SnnMnSePD99qkiObeHvLA2RP2mAfA0SThcLketokrkQxNpoTu9ZKw9+TzLmE1WGOQdL2T9FpGmKAPxmIx323EQ0NDtLu7m7W0tPgkSjq9BDQnejyFh/fHPMckSjsNw2DIUeG0HxDJZHx8XFpYWGCkDszlsucYiwRJPczNzcmlUknq7++nLjF2Ojo6aCQSYZYQOa/F5at5T8GFdMZzzBJ8Brmy2aw0MjJCXGLoUE3T2PLyMtO4Pu4lYPL97ze02lxSyTREthd0bl4n68HlWmx/zM7O2j/nzNUxLwEapEzmpWHXOnNZJUuXJ0nm2Cf2mAfEdaP4A1kPLOo+ent75UwmowB5+GjTfe0fHHwhxYgUIbsDcSY/euSr3MX/W1tbV4FDQ53dPJYkCRNb/KHOLOXUxW/JLuGaWvji7OxYrqGhAQ8PNNLmsYkTiQR3iDlku3V66tdvYF/y5A5hwN4m/z3zOcQPX1lZ4WAtr4zZ6ZNOpykMoBJMlmVftjQvFi3tz8ONnQlGd+ZyVPzTmfSrE8b8vN/vL5umqcXjcaOvr89MpVKiOm+RWIIJLBAIyFeKufKCWb4E5E/LlG2LXOPGjeHp3177sZCZhoMDScuwv1o+n0dSC+dUVycGx1oALA9CWjWAliFd18Pw33+uZ+CVA6G7Xyab3FhMbq1MqLMjp2dS342Xbs4DaUlRlFVVVVdgGPNQJ06hoDUWY7UKQAvBgjDnPATneBCa77m77m8/Gj34UHdwz7MK8+8JSCy2Zp11c8ksT+T0wj+f5X7/+b+lXNHn8xloKQyXoK06b4xmgzjVySXGQpFMJvFkkaPRaBCsDcIRF0IlQBAqI4MwmaxXNFwrICYouNK2AuaZaDjMQ5JSKBQqIZAUTkcDZFukanE1sI/7jpVEcRoewgoI9VfIkayyFkiJ4z4LiR1SFV3b1NSkFotF1bHUIlUXgXpFwbYiHA5zEMYRQMgtyzLh04Jmvx2h2FToq8FgsAzBWYY1KqSRBnlrwBnNq0k3srgCiazvuc9ptsWw9zIEC0a+BHJtBeEfh38WKKkzxnQITAOqESpjkvVbx5aIaZUC6BUG6cDQzYuLi6xKMQEnkoBMEI4rTcxVsBC/OcQNd26t24Z9HXLI0WIFyifuebjS2trawpCGGISK4xk7ADe60m4bKMQRZLsfi0rlDdFqe8R5u0G3FYt2go3WbcultwBGUU9+kE6VewAAAABJRU5ErkJggg=='})

        var config = {
            crs: "EPSG:3857",
            format: "png",
            name: "standaard",
            layerName: "standaard",
            type: "wmts",
            minZoom: 10,
            maxZoom: 19,
            tileSize: 256,
            attribution: "",
        }

        L.tileLayer(url, config).addTo(map);

        const resizeObserver = new ResizeObserver(() => {
            console.log('resizeObserver')
            map.invalidateSize();

            let markerSelectedEvent = new CustomEvent('markerDeselectedEvent', { bubbles: true, cancelable: false, detail: {}});
            self.element.dispatchEvent(markerSelectedEvent);
            map.closePopup()
        });

        resizeObserver.observe(mapDiv);

        //create the marker group
        markers = new L.featureGroup();
        //add the markers to the map
        map.addLayer(markers);
        //fit the map to the markers

        buurten =  L.tileLayer.wms('https://service.pdok.nl/cbs/wijkenbuurten/2022/wms/v1_0?request=GetCapabilities&service=WMS', {
            layers: 'buurten',
            format:'image/png',
            transparent: true,
            minZoom: 10,
            maxZoom: 19,
            srsName: "EPSG:4326",
            bbox: "51.9247770, 4.4780970, 51.9247774, 4.4780974",
        })
    }

    toggleBuurten(e) {
        console.log("toggle buurten", e)
        e.target.classList.toggle("active")
        if(map.hasLayer(buurten)) {
            map.removeLayer(buurten)

        }else {
            buurten.addTo(map)
        }

    }

    verbergBuurten() {
        map.removeLayer(buurten)
    }

    makeRoute(event) {
        console.log("makeRoute")
        // let routeUrl = "https://www.google.com/maps/dir"
        // let routeUrl = 'https://www.waze.com/ul?ll=40.75889500,-73.98513100&navigate=yes&zoom=17'
        let routeUrl = 'https://www.waze.com/ul?ll='

        function handleCurrentLocation(pos) {
            console.log("handleCurrentLocation, pos", pos)
            const crd = pos.coords;
            routeUrl += `/${crd.latitude}+${crd.longitude}`
            getRoute(event)
        }

        function handleNoCurrentLocation(error) {
            console.log("handleNoCurrentLocation")
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
            getRoute(event)
        }

        function getRoute(event) {
            let lat = event.params.lat
            let long = event.params.long

            routeUrl += `${lat},${long}&navigate=yes`
            console.log('getRoute: ', routeUrl)
            window.open(routeUrl, "_blank")
        }

        // navigator.geolocation.getCurrentPosition(handleCurrentLocation, handleNoCurrentLocation);
        getRoute(event)
    }

    plotMarkers(coordinatenlijst) {
        console.log("plot markers, coordinatenlijst", coordinatenlijst)
        if(coordinatenlijst){
            for(let i = 0; i<coordinatenlijst.length; i++){
                const lat = coordinatenlijst[i].geometrie.coordinates[1]
                const long = coordinatenlijst[i].geometrie.coordinates[0]
                const adres = coordinatenlijst[i].adres;
                const afbeelding = coordinatenlijst[i].afbeeldingUrl;
                const omschrijving = coordinatenlijst[i].onderwerpen;
                const taakId = coordinatenlijst[i].taakId

                const markerLocation = new L.LatLng(lat, long);
                const marker = new L.Marker(markerLocation, {icon: markerGreen, taakId: taakId});
                const paragraphDistance = `<p>Afstand: <span data-incidentlist-target="taakAfstand" data-latitude="${lat}" data-longitude="${long}"></span> meter</p>`

                // let popupContent = `<div class="container__content"><a href="/taak/${taakId}" target="_top" aria-label="Bekijk taak ${taakId}">${adres}</a><p>${omschrijving}</p>${paragraphDistance}</div>`
                let popupContent = `<div class="container__content"><span class="link" data-action="click->kaart#makeRoute" data-kaart-lat-param="${lat}" data-kaart-long-param="${long}" aria-label="Bekijk taak ${taakId}">${adres}</span><p>${omschrijving}</p>${paragraphDistance}</div>`
                if (afbeelding) {
                    // popupContent = `<div class="container__image"><img src=${afbeelding}></div><div class="container__content"><a href="/taak/${taakId}" target="_top" aria-label="Bekijk taak ${taakId}">${adres}</a><p>${omschrijving}</p>${paragraphDistance}</div>`
                    popupContent = `<div class="container__image"><img src=${afbeelding}></div><div class="container__content"><span class="link" data-action="click->kaart#makeRoute" data-kaart-lat-param="${lat}" data-kaart-long-param="${long}" aria-label="Bekijk taak ${taakId}">${adres}</span><p>${omschrijving}</p>${paragraphDistance}</div>`
                }
                marker.bindPopup(popupContent)

                markers.addLayer(marker)
                markerList.push(marker)
            }
        }
    }
}
