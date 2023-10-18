import { Controller } from '@hotwired/stimulus';

let showSortingContainer = false;
let sortDirectionReversed = false;
let mapHasBeenLoaded = false
let markers = null
let markerIcon, markerBlue, markerGreen, markerMagenta = null
let currentLocation = [51.924421, 4.477727] //hofplein

export default class extends Controller {

    static values = {
        kaart: Object,
    }
    static targets = [ "sorting", "toggleMapView" ]

    initialize() {
        const mapDiv = document.getElementById('incidentMap')
        if(mapDiv){
            const map = L.map('incidentMap')

            console.log("draw map")
            const coordinatenlijst = this.kaartValue.kaart_taken_lijst

            markerIcon = L.Icon.extend({
                options: {
                    iconSize:     [26, 26],
                    iconAnchor:   [13, 13],
                    popupAnchor:  [0, -17]
                }
            });

            markerGreen = new markerIcon({iconUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAASTSURBVHgBrZZNbBtFFMf/O7vrr42xGylKQ9PU4YDaHCDtiVtSIVFEL+WQcGvFqSAkEAghDlXrqL1xQEJCqDkgDiAhRXwKSotEUziAxAEipEQgRY2BBEdKGtuJY6/t3Rne26w/Gnmdz2c97+7Mzvu99+bNzGrYraRTSWjyEjRtFArD1JLyezJbqj6CEj8incnsxpy24xtvDxxBVLxGhkmR3PF9qAlc+ye901udwddPDELiLprR7VYWUMPTuPH3QtALYnuDUkrzHLqybyjLIEz8QNOTIns7gxlKojywuW9oE66pu9obx7v9YILBDE2n04I8vXZAaBOeMF71otkG3+6JFr5y/LGKKeZxeJLDUvVxTGYf0H0j72KbE6KiibOdrKQS/Zi++Clyb/0BdTWDz8dvem0dJImjoUs+SwsEQ1cXO0F/v3wLo6mnkIw84rU9f/Icfrv8bSe4Rr+RtuBGJQMGXU4EWXj33NUGsFWORBL48MI7QDD6ib6+PhPbwRMTE9rQ0JDe3d1tUtdA0PgLJ58JtD3cO4QO4IFaraYzo870/qiSMTc3J9bW1nR0kLy9HtjXLhOtsrq6apRKJTE2NqY1wPzQ39+vxeNxHVItBg2eWZ4LNPzVX98H9pHNf5mVyWTE1NQUGmB60CqVir6xsaHDUYHWX/z6zbZR5+wCXr9zHYHiqCU0i6sRsXezsrKy1ViUvwaNz+QXcXryOXzpR8dOTGd+wZnJ815fgCjk3S/QLCyt8Tc6OmrMzs5GCG7hVOwYXui5Rz1xHI4o3CucxXT+z56enk1iVKjNaaxjIQTvKip8313HmvMJDkseODfDP5cXu7q6JD9SkB7HA4+MjEgfLGlbdfHN2sc0L//hoOLS3L639AHVjywWi5KilfWu+jpGNpvlRtfT++U8vsu9fCA4j72deykUCjnRaLTGdlOplKSIPXjrhPPOEia1wuFwnLy0cCY+iPNH3oeh9WEv4qisfnv9FTGzuUAbR5FaNvz5rdI9O6Ee2jBoWxOUakELXSdPhbtYLuOnwmc4ZQl06cPY6YtFqiKyVB9TKzeM+eoyQe1IJGI7jmOTTYY68E+oVkOcdsOPOkYDLClljPbxKKmpnrSOuUOR03jUfBYhcbSRBUcto6zmkavN4E7uFhYrBdM0iVkrU2+JdNO/VurRPgTmg2J8fJx3FiOZTEar1WqUvIyxE2SInTHImIHmicZjlWEYGkXE86boPY7IofcYUorFYiUWhtLuWCPbLloGtwo/c/p5viO+RvlKRkN1OMPqYwnqJZnUZbAPtUnLiUTCLhQKth+pi5YPgU6HgheFZVmSjEkWAkrXdR26dUm9q2+U1aZnmyq4TMVZ5vmlAq1QFddoj5at0HYR10WgOeemr17ENPeGbds6GRdk13OQ2iS1ueRkVdf1KhVmjU4jdsapB7BbsNbiAGdFp+Wgc5rz+bze4piiHUnR5qD8VDq0VjlCvpdUN9L/at2zbH0ObcE54ggdnzznVl17e3stWoZchBE/M14Btvuk3bOwEd+Ql34+VOpXqlYvI/61UXS7iWg/0m7cnlL6P5qNFK3aTp7nAAAAAElFTkSuQmCC'})
            markerBlue = new markerIcon({iconUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAATESURBVHgBrVZNTGNVFL7vp9AfCB0mpAOSoRgdGUQcI8yiCYImGjXExBBYGbshcdGiKxHHhSVRdG+M0YWrccUC4qSz0EQT2RATiNHEBFKcjnYmg6BtLfa/7/qdx72vr50OU+qc5OTed9895zvn3HPOvYw1SZxzL/gt8Br4Bq8Szb8HB8F+9qAolUqdgcIIOMmbowj7vwQlg3XeNUu/5XK5wZN0Kw3AFBCDoN/pdH6HJb/8t3GTsWu7nEV3GbuZOl4b9TH2BPjKhMIGvDWqboCfA8dJ34nAApRjqmK+J0FTecY+2uDs0x/ZiRS6fGxAl7MKnkgkxvr7+5NCr0VqjRX4GYlE1Eql8r4d9KWr9wcloj0vY286by0N9vX1vWl6A6dqsOpkFSTTw11dXTG58M63zYHaKQzPP37eUp3c2tq6MDY29hfmltdqnRGqw+F4Vi7QOZ4WlIhkKB8EeUdGRoICS7kncFtb2+tyYWWDs1aIpKK7lqyiadpkQ2ARf2JdVdUB+fOXO6xlurZTnUPnaG9vr+Mu4OXlZWV4eFjr7u52YNN5+fPnP1nL9Hu6Bvh8qVTSCENiKjYD2sAueP+3FOj4sLVQS8WZ9ywHqU7P+v3+3Pj4eGl1dbVios/OziqoNaWzs1ODZQm5e6CLtUzUVCShPP/AoMbjcRWg5poJjA+lUChomUxGQ8f6VQpMX2At06gNGLpvsWpyKcz2wQ4ODszF/f19q4CmH1NYK0RS7z5TDXMsFltj1WO1gPnU1BTr6emhA+VLS0trCE2Gfk4gv0Pj7NQUuqzUHNP6+jo5owDDArfqGJlnAkej0X9g4Vdy/Qosf9LHmiYK8dJE9XtnZ+fzlZWVREdHh0HfcNLEMYEnJycNAWwg+yoLCwtX8/n8bfpHDf/6awoLjze4yhp4Snu94pKgsx0aGvoMo3F0dGTgOI16GTKAtp/BVUh1/Hg4HH4FiXbLfsnGU5y/8bXBA18Y3PPBMQ9/YvC3vzH4D/HaC5lkQ6HQNDrhsMvl6odOL8rJSZeQHZicoTruBJ9rb29/FOOl+fn5V7PZ7G1+SiIZkkXfvwQ9j4B9ON8OgXFX4DS0NTdq+SzmA7D0IsYxcGB7e/tL6DPuB4gekKG9gUDgBYA+DdmLIoLdYBdhSGClLtw6uB3shoDHMAw39FE3cwSDwYdmZmaeQud50ePxnEP4ekkIIb2TTCZje3t7Py0uLl7f3NxMAxQ2lHL4nQX/K8YCuMTE1VgtNlwUc3Nz1Fl0r9frKhaLLoTMTUZAERmjQ5nOqjcayXJd15VyuUxJw7GvjLGMfQSSdbvdWSICRXc0W6X9bOvPmsLhEMnmFCFyQmmbBCcwKQtQGgi4QsAClN4gOTwo8um0+R4hTyvM9hDQ2L3J9AJhNaDMIAKggeZSxrQCNkehlDiP7zyOIIfkzEEmjzIqoG5L6NGGHbSRx5JUVj1zh2DTY5y9jhrXoFyFXtNArBlYq8DIIi79IhKzdHh4SMaUpQPNAtuvS4qKhnKgm0vHm0yzGcbRkTiaAxehLKNWyUOaUxUY9a/LZsl8Dglw8tiJ65PO3CPZ5/N5qAzZcT44RJTU+ldlS0RKhCIz/Dg3XY7IVjMiYrSSrhmPWqFGcqcK6X9czfgLQYqNowAAAABJRU5ErkJggg=='})
            markerMagenta = new markerIcon({iconUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAATuSURBVHgBrVZNbBtFFJ7ZWdtrO06ciJBaCakbaCuigAqI8iOE03JBSIhc4gMSDQcOHIC2CKRegARxQAiVcEAI6AG1ICFyQAIJCaEWWwUaIlUgqCOkRombuG6l/DjOj72/M31vs95Ybtb5aT5pdnd2Zt733pv35g0lW8Tfh05ENZ9vgFLaC91DhIj42gjNUiGygtKvuSSlnxj9MLsVeXSzCRefOtXs163jQojjQBolm4IOPTb20eCms+oN/nX4rX0w5QJ8xsn2MKUS8Uxi7OMprwlS7Q+wDJWh6Z2TIvYphJ6/9PipOMjbnBhJATiTKjsndcklbl345ck3WxxjvImRdHBwUBp99O337pDUJY9y+Q3bmhryWk3o+Ude72pgygTZJYD7CpNW8cCLl7+cX+uuQa5RQvIxdqSeIH+smXS9mySh/e1EjiikkLpCrg3/RPQbhQ3ng9DoPVJkAD6HofEKuVRLLAv5WD3SnnMnSePD99qkiObeHvLA2RP2mAfA0SThcLketokrkQxNpoTu9ZKw9+TzLmE1WGOQdL2T9FpGmKAPxmIx323EQ0NDtLu7m7W0tPgkSjq9BDQnejyFh/fHPMckSjsNw2DIUeG0HxDJZHx8XFpYWGCkDszlsucYiwRJPczNzcmlUknq7++nLjF2Ojo6aCQSYZYQOa/F5at5T8GFdMZzzBJ8Brmy2aw0MjJCXGLoUE3T2PLyMtO4Pu4lYPL97ze02lxSyTREthd0bl4n68HlWmx/zM7O2j/nzNUxLwEapEzmpWHXOnNZJUuXJ0nm2Cf2mAfEdaP4A1kPLOo+ent75UwmowB5+GjTfe0fHHwhxYgUIbsDcSY/euSr3MX/W1tbV4FDQ53dPJYkCRNb/KHOLOXUxW/JLuGaWvji7OxYrqGhAQ8PNNLmsYkTiQR3iDlku3V66tdvYF/y5A5hwN4m/z3zOcQPX1lZ4WAtr4zZ6ZNOpykMoBJMlmVftjQvFi3tz8ONnQlGd+ZyVPzTmfSrE8b8vN/vL5umqcXjcaOvr89MpVKiOm+RWIIJLBAIyFeKufKCWb4E5E/LlG2LXOPGjeHp3177sZCZhoMDScuwv1o+n0dSC+dUVycGx1oALA9CWjWAliFd18Pw33+uZ+CVA6G7Xyab3FhMbq1MqLMjp2dS342Xbs4DaUlRlFVVVVdgGPNQJ06hoDUWY7UKQAvBgjDnPATneBCa77m77m8/Gj34UHdwz7MK8+8JSCy2Zp11c8ksT+T0wj+f5X7/+b+lXNHn8xloKQyXoK06b4xmgzjVySXGQpFMJvFkkaPRaBCsDcIRF0IlQBAqI4MwmaxXNFwrICYouNK2AuaZaDjMQ5JSKBQqIZAUTkcDZFukanE1sI/7jpVEcRoewgoI9VfIkayyFkiJ4z4LiR1SFV3b1NSkFotF1bHUIlUXgXpFwbYiHA5zEMYRQMgtyzLh04Jmvx2h2FToq8FgsAzBWYY1KqSRBnlrwBnNq0k3srgCiazvuc9ptsWw9zIEC0a+BHJtBeEfh38WKKkzxnQITAOqESpjkvVbx5aIaZUC6BUG6cDQzYuLi6xKMQEnkoBMEI4rTcxVsBC/OcQNd26t24Z9HXLI0WIFyifuebjS2trawpCGGISK4xk7ADe60m4bKMQRZLsfi0rlDdFqe8R5u0G3FYt2go3WbcultwBGUU9+kE6VewAAAABJRU5ErkJggg=='})

            var url = "https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{layerName}/{crs}/{z}/{x}/{y}.{format}";
            // var url = "https://service.pdok.nl/cbs/wijkenbuurten/2022/wfs/v1_0?request=GetCapabilities&service=WFS"

            var config = {
                crs: "EPSG:3857",
                format: "png",
                name: "standaard",
                layerName: "standaard",
                type: "wmts",
                minZoom: 6,
                maxZoom: 19,
                tileSize: 256,
                attribution: "",
            }

            L.tileLayer(url, config).addTo(map);
            // L.tileLayer.wms('https://service.pdok.nl/cbs/wijkenbuurten/2022/wms/v1_0?request=GetCapabilities', {
            //     layers: 'buurten',
            //     format:'image/png',
            //     transparent: true
            // }).addTo(map);

            const resizeObserver = new ResizeObserver(() => {
                console.log('resizeObserver')
                // map.invalidateSize();
            });

            resizeObserver.observe(mapDiv);


            //create the marker group
            markers = new L.featureGroup();
            this.plotMarkers(coordinatenlijst);
            //add the markers to the map
            map.addLayer(markers);
            //fit the map to the markers
            map.fitBounds(markers.getBounds());

            // mapHasBeenLoaded = true
        }
    }

    connect(e) {
        // mapHasBeenLoaded = false
        if(this.hasSortingTarget && showSortingContainer === true ) {
            this.sortingTarget.classList.remove("hidden-vertical")
            this.sortingTarget.classList.add("show-vertical")
        }
    }

    disconnect() {
        console.log("disconnect")
    }

    plotMarkers(coordinatenlijst) {
        console.log("plot markers, coordinatenlijst", coordinatenlijst)
        if(coordinatenlijst){
            navigator.geolocation.getCurrentPosition(this.handleCurrentLocation, this.handleNoCurrentLocation);

            for(let i = 0; i<coordinatenlijst.length; i++){
                const lat = coordinatenlijst[i].geometrie.coordinates[1]
                const long = coordinatenlijst[i].geometrie.coordinates[0]

                const adres = coordinatenlijst[i].adres;
                const afbeelding = coordinatenlijst[i].afbeelding;
                const omschrijving = coordinatenlijst[i].omschrijving;
                const taakId = coordinatenlijst[i].taak_id
                let showImage = false

                if(typeof(afbeelding) === 'string') showImage = true
                    const markerLocation = new L.LatLng(lat, long);
                    const marker = new L.Marker(markerLocation, {icon: markerGreen});
                    const distance = `Afstand: ${(Math.round(markerLocation.distanceTo(currentLocation)))} meter`
                if (showImage) {
                    marker.bindPopup(`<div class="container__image"><img src=${afbeelding}></div><div class="container__content"><a href="/taak/${taakId}" target="_top" aria-label="Bekijk taak ${taakId}">${adres}</a><p>${omschrijving}</p><p>${distance}</p></div>`);
                }else{
                    marker.bindPopup(`<div class="container__content"><a href="/taak/${taakId}" target="_top" aria-label="Bekijk taak ${taakId}">${adres}</a><p>${omschrijving}</p><p>${distance}</p></div>`);
                }
                markers.addLayer(marker);
            }

            const markerCurrent = new L.Marker(currentLocation, {icon: markerBlue});
            markers.addLayer(markerCurrent)
        }
    }

    toggleMapView(e) {
        document.getElementById('taken_lijst').classList.toggle('showMap')

        const frame = document.getElementById('taken_lijst');
        console.log("frame", frame)
        frame.reload()

    }
    handleCurrentLocation(pos) {
        const crd = pos.coords;
        console.log("handleCurrentLocation, pos.coords:", pos.coords)
        if(pos.coords){
            currentLocation = [pos.coords.latitude, pos.coords.longitude]
        }
    }

    handleNoCurrentLocation(error) {
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
