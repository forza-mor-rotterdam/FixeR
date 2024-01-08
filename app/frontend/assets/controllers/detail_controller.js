import { Controller } from '@hotwired/stimulus';

let markerIcon, markerBlue, markerGreen, markerMagenta, markerMe, markers, map, currentImg, imageContainer, modal, modalBackdrop, isMobileDevice, currentPosition = null
let dist, elapsedTime, startX, startY, startTime = 0
let imageSrcList = []

let self = null
export default class extends Controller {
    static outlets = ["kaart"];
    static values = {
        incidentX: String,
        incidentY: String,
        areaList: String,
        currentDistrict: String,
        incidentObject: Object,
        mercurePublicUrl: String,
        mercureSubscriberToken: String,
    }
    static targets = ['selectedImage', 'thumbList', 'imageSliderContainer', 'taakAfstand', 'navigeerLink']

    Mapping = {
        'fotos': 'media',
    };

    initialize() {
        let self = this
        let childControllerConnectedEvent = new CustomEvent('childControllerConnectedEvent', { bubbles: true, cancelable: false, detail: {
            controller: self
        }});

        window.dispatchEvent(childControllerConnectedEvent);
        self.initMessages()

        if(self.hasThumbListTarget) {
            self.thumbListTarget.getElementsByTagName('li')[0].classList.add('selected')
        }

        const mapDiv = document.getElementById('incidentMap')
        if(mapDiv){
            markers = new L.featureGroup();
            markerIcon = L.Icon.extend({
                options: {
                    iconSize:     [26, 26],
                    iconAnchor:   [13, 13],
                    popupAnchor:  [0, -17]
                }
            });

            markerGreen = new markerIcon({iconUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAASTSURBVHgBrZZNbBtFFMf/O7vrr42xGylKQ9PU4YDaHCDtiVtSIVFEL+WQcGvFqSAkEAghDlXrqL1xQEJCqDkgDiAhRXwKSotEUziAxAEipEQgRY2BBEdKGtuJY6/t3Rne26w/Gnmdz2c97+7Mzvu99+bNzGrYraRTSWjyEjRtFArD1JLyezJbqj6CEj8incnsxpy24xtvDxxBVLxGhkmR3PF9qAlc+ye901udwddPDELiLprR7VYWUMPTuPH3QtALYnuDUkrzHLqybyjLIEz8QNOTIns7gxlKojywuW9oE66pu9obx7v9YILBDE2n04I8vXZAaBOeMF71otkG3+6JFr5y/LGKKeZxeJLDUvVxTGYf0H0j72KbE6KiibOdrKQS/Zi++Clyb/0BdTWDz8dvem0dJImjoUs+SwsEQ1cXO0F/v3wLo6mnkIw84rU9f/Icfrv8bSe4Rr+RtuBGJQMGXU4EWXj33NUGsFWORBL48MI7QDD6ib6+PhPbwRMTE9rQ0JDe3d1tUtdA0PgLJ58JtD3cO4QO4IFaraYzo870/qiSMTc3J9bW1nR0kLy9HtjXLhOtsrq6apRKJTE2NqY1wPzQ39+vxeNxHVItBg2eWZ4LNPzVX98H9pHNf5mVyWTE1NQUGmB60CqVir6xsaHDUYHWX/z6zbZR5+wCXr9zHYHiqCU0i6sRsXezsrKy1ViUvwaNz+QXcXryOXzpR8dOTGd+wZnJ815fgCjk3S/QLCyt8Tc6OmrMzs5GCG7hVOwYXui5Rz1xHI4o3CucxXT+z56enk1iVKjNaaxjIQTvKip8313HmvMJDkseODfDP5cXu7q6JD9SkB7HA4+MjEgfLGlbdfHN2sc0L//hoOLS3L639AHVjywWi5KilfWu+jpGNpvlRtfT++U8vsu9fCA4j72deykUCjnRaLTGdlOplKSIPXjrhPPOEia1wuFwnLy0cCY+iPNH3oeh9WEv4qisfnv9FTGzuUAbR5FaNvz5rdI9O6Ee2jBoWxOUakELXSdPhbtYLuOnwmc4ZQl06cPY6YtFqiKyVB9TKzeM+eoyQe1IJGI7jmOTTYY68E+oVkOcdsOPOkYDLClljPbxKKmpnrSOuUOR03jUfBYhcbSRBUcto6zmkavN4E7uFhYrBdM0iVkrU2+JdNO/VurRPgTmg2J8fJx3FiOZTEar1WqUvIyxE2SInTHImIHmicZjlWEYGkXE86boPY7IofcYUorFYiUWhtLuWCPbLloGtwo/c/p5viO+RvlKRkN1OMPqYwnqJZnUZbAPtUnLiUTCLhQKth+pi5YPgU6HgheFZVmSjEkWAkrXdR26dUm9q2+U1aZnmyq4TMVZ5vmlAq1QFddoj5at0HYR10WgOeemr17ENPeGbds6GRdk13OQ2iS1ueRkVdf1KhVmjU4jdsapB7BbsNbiAGdFp+Wgc5rz+bze4piiHUnR5qD8VDq0VjlCvpdUN9L/at2zbH0ObcE54ggdnzznVl17e3stWoZchBE/M14Btvuk3bOwEd+Ql34+VOpXqlYvI/61UXS7iWg/0m7cnlL6P5qNFK3aTp7nAAAAAElFTkSuQmCC'})
            markerBlue = new markerIcon({iconUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAATESURBVHgBrVZNTGNVFL7vp9AfCB0mpAOSoRgdGUQcI8yiCYImGjXExBBYGbshcdGiKxHHhSVRdG+M0YWrccUC4qSz0EQT2RATiNHEBFKcjnYmg6BtLfa/7/qdx72vr50OU+qc5OTed9895zvn3HPOvYw1SZxzL/gt8Br4Bq8Szb8HB8F+9qAolUqdgcIIOMmbowj7vwQlg3XeNUu/5XK5wZN0Kw3AFBCDoN/pdH6HJb/8t3GTsWu7nEV3GbuZOl4b9TH2BPjKhMIGvDWqboCfA8dJ34nAApRjqmK+J0FTecY+2uDs0x/ZiRS6fGxAl7MKnkgkxvr7+5NCr0VqjRX4GYlE1Eql8r4d9KWr9wcloj0vY286by0N9vX1vWl6A6dqsOpkFSTTw11dXTG58M63zYHaKQzPP37eUp3c2tq6MDY29hfmltdqnRGqw+F4Vi7QOZ4WlIhkKB8EeUdGRoICS7kncFtb2+tyYWWDs1aIpKK7lqyiadpkQ2ARf2JdVdUB+fOXO6xlurZTnUPnaG9vr+Mu4OXlZWV4eFjr7u52YNN5+fPnP1nL9Hu6Bvh8qVTSCENiKjYD2sAueP+3FOj4sLVQS8WZ9ywHqU7P+v3+3Pj4eGl1dbVios/OziqoNaWzs1ODZQm5e6CLtUzUVCShPP/AoMbjcRWg5poJjA+lUChomUxGQ8f6VQpMX2At06gNGLpvsWpyKcz2wQ4ODszF/f19q4CmH1NYK0RS7z5TDXMsFltj1WO1gPnU1BTr6emhA+VLS0trCE2Gfk4gv0Pj7NQUuqzUHNP6+jo5owDDArfqGJlnAkej0X9g4Vdy/Qosf9LHmiYK8dJE9XtnZ+fzlZWVREdHh0HfcNLEMYEnJycNAWwg+yoLCwtX8/n8bfpHDf/6awoLjze4yhp4Snu94pKgsx0aGvoMo3F0dGTgOI16GTKAtp/BVUh1/Hg4HH4FiXbLfsnGU5y/8bXBA18Y3PPBMQ9/YvC3vzH4D/HaC5lkQ6HQNDrhsMvl6odOL8rJSZeQHZicoTruBJ9rb29/FOOl+fn5V7PZ7G1+SiIZkkXfvwQ9j4B9ON8OgXFX4DS0NTdq+SzmA7D0IsYxcGB7e/tL6DPuB4gekKG9gUDgBYA+DdmLIoLdYBdhSGClLtw6uB3shoDHMAw39FE3cwSDwYdmZmaeQud50ePxnEP4ekkIIb2TTCZje3t7Py0uLl7f3NxMAxQ2lHL4nQX/K8YCuMTE1VgtNlwUc3Nz1Fl0r9frKhaLLoTMTUZAERmjQ5nOqjcayXJd15VyuUxJw7GvjLGMfQSSdbvdWSICRXc0W6X9bOvPmsLhEMnmFCFyQmmbBCcwKQtQGgi4QsAClN4gOTwo8um0+R4hTyvM9hDQ2L3J9AJhNaDMIAKggeZSxrQCNkehlDiP7zyOIIfkzEEmjzIqoG5L6NGGHbSRx5JUVj1zh2DTY5y9jhrXoFyFXtNArBlYq8DIIi79IhKzdHh4SMaUpQPNAtuvS4qKhnKgm0vHm0yzGcbRkTiaAxehLKNWyUOaUxUY9a/LZsl8Dglw8tiJ65PO3CPZ5/N5qAzZcT44RJTU+ldlS0RKhCIz/Dg3XY7IVjMiYrSSrhmPWqFGcqcK6X9czfgLQYqNowAAAABJRU5ErkJggg=='})
            markerMagenta = new markerIcon({iconUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMy43NzgzIDYuMjI0MTJDMTkuNTAwMyAxLjk0NjEzIDEyLjQ5OTkgMS45NDYxMyA4LjIyMTkzIDYuMjI0MTJDMy45NDM5MyAxMC41MDIxIDMuOTQzOTMgMTcuNTAyNSA4LjIyMTkzIDIxLjc4MDVMMTYuMDAwMSAyOS41NTg2TDIzLjc3ODMgMjEuNzgwNUMyOC4wNTYzIDE3LjUwMjUgMjguMDU2MyAxMC41MDIxIDIzLjc3ODMgNi4yMjQxMlpNMTYuMDAwMSAxOC4wMDIzQzE4LjIwOTIgMTguMDAyMyAyMC4wMDAxIDE2LjIxMTQgMjAuMDAwMSAxNC4wMDIzQzIwLjAwMDEgMTEuNzkzMiAxOC4yMDkyIDEwLjAwMjMgMTYuMDAwMSAxMC4wMDIzQzEzLjc5MSAxMC4wMDIzIDEyLjAwMDEgMTEuNzkzMiAxMi4wMDAxIDE0LjAwMjNDMTIuMDAwMSAxNi4yMTE0IDEzLjc5MSAxOC4wMDIzIDE2LjAwMDEgMTguMDAyM1oiIGZpbGw9IiNDOTM2NzUiLz4KPC9zdmc+Cg=='})


            var url = "https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{layerName}/{crs}/{z}/{x}/{y}.{format}";
            var config = {
                crs: "EPSG:3857",
                format: "png",
                name: "standaard",
                layerName: "standaard",
                type: "wmts",
                minZoom: 12,
                maxZoom: 19,
                tileSize: 256,
                attribution: "",
            }
            const incidentCoordinates = [parseFloat(self.incidentXValue.replace(/,/g, '.')), parseFloat(self.incidentYValue.replace(/,/g, '.'))]
            map = L.map('incidentMap').setView(incidentCoordinates, 18);
            L.tileLayer(url, config).addTo(map);
            const marker = L.marker(incidentCoordinates, {icon: markerMagenta}).addTo(map);

            markers.addLayer(marker);

            if(currentPosition) {
                markerMe = new L.Marker(
                    [currentPosition[0], currentPosition[1]],
                    { icon: markerBlue }
                );
                markers.addLayer(markerMe);
                markerMe.setLatLng([currentPosition[0], currentPosition[1]]);
                L.marker(currentPosition, {icon: markerBlue}).addTo(map);
                map.fitBounds(markers.getBounds())
            }

            window.addEventListener("positionChangeEvent", function(e){
                self.positionWatchSuccess(e.detail.position)
            });
        }
    }

    connect() {
        document.querySelectorAll(".container__image").forEach(element => {
            this.pinchZoom(element);
        });

        const touchsurface = document.querySelector('#container-image'),
        threshold = 150, //required min distance traveled to be considered swipe
        allowedTime = 1000 // maximum time allowed to travel that distance
        if (touchsurface){

            touchsurface.addEventListener('touchstart', function(e){
                var touchobj = e.changedTouches[0]
                dist = 0
                startX = touchobj.pageX
                startY = touchobj.pageY
                startTime = new Date().getTime() // record time when finger first makes contact with surface
                e.preventDefault()
            }, false)

            touchsurface.addEventListener('touchmove', function(e){
                e.preventDefault() // prevent scrolling when inside DIV
            }, false)

            touchsurface.addEventListener('touchend', function(e){
                var touchobj = e.changedTouches[0]
                dist = touchobj.pageX - startX // get total dist traveled by finger while in contact with surface
                elapsedTime = new Date().getTime() - startTime // get time elapsed
                // check that elapsed time is within specified, horizontal dist traveled >= threshold, and vertical dist traveled <= 100
                var swiperightBol = (elapsedTime <= allowedTime && dist >= threshold && Math.abs(touchobj.pageY - startY) <= 100)
                self.handleswipe(swiperightBol)
                e.preventDefault()
            }, false)
        }
    }

    disconnect(){

    }

    taakAfstandTargetConnected(element) {
        const markerLocation = new L.LatLng(element.dataset.latitude, element.dataset.longitude);
        element.textContent = Math.round(markerLocation.distanceTo(currentPosition))
    }

    positionChangeEvent(position) {
        console.log("DETAIL, positionChangeEvent lat", position.coords.latitude)
        console.log("DETAIL, positionChangeEvent long", position.coords.longitude)

    }

    positionWatchSuccess(position){
        let self = this
        console.log("detail.positionWatchSuccess")
        currentPosition = [position.coords.latitude, position.coords.longitude]
       if (self.hasTaakAfstandTarget){
            const elem = self.taakAfstandTarget
            const markerLocation = new L.LatLng(elem.dataset.latitude, elem.dataset.longitude);
            const afstand = Math.round(markerLocation.distanceTo(currentPosition))
            elem.textContent = afstand
        }
        if (self.hasNavigeerLinkTarget){
            const linkList = document.querySelectorAll('[data-detail-target="navigeerLink"]')

            for (const link of linkList) {
                const href = link.getAttribute("href")
                const rx = new RegExp("saddr=[\\d\\D]*?&", "g");
                const newHref = href.replace(rx, `saddr=${currentPosition}&`);
                link.setAttribute('href', newHref)
            }
        }
    }

    makeRoute(event) {
        // let routeUrl = "https://www.google.com/maps/dir"
        // let routeUrl = 'https://www.waze.com/ul?ll=40.75889500,-73.98513100&navigate=yes&zoom=17'
        let routeUrl = "https://www.waze.com/ul?ll=";


        function getRoute(event) {
          let lat = event.params.lat;
          let long = event.params.long;
          routeUrl += `${lat},${long}&navigate=yes`;
          window.open(routeUrl, "_blank");
        }

        getRoute(event);
      }

    isValidHttpUrl(string) {
        let url;

        try {
          url = new URL(string);
        } catch (_) {
          return false;
        }

        return url.protocol === "http:" || url.protocol === "https:";
    }
    initMessages(){
        let self = this
        if (self.hasMercurePublicUrlValue && self.isValidHttpUrl(self.mercurePublicUrlValue)){
            const url = new URL(self.mercurePublicUrlValue);
            url.searchParams.append('topic', window.location.pathname);
            if (self.hasMercureSubscriberTokenValue){
                url.searchParams.append('authorization', self.mercureSubscriberTokenValue);
            }
            console.log(url)
            self.eventSource = new EventSource(url);
            self.eventSource.onmessage = e => self.onMessage(e)
            self.eventSource.onerror = (e) => self.onMessageError(e)
        }
    }
    onMessage(e){
        let data  = JSON.parse(e.data)
        console.log("mercure message", data)
        let turboFrame = document.getElementById("taak_basis")
        turboFrame.src = data.url
    }
    onMessageError(e){
        let self = this
        console.log(e)
        console.log("An error occurred while attempting to connect.");
        self.eventSource.close()
    }
    handleswipe(isrightswipe){
        const imgIndex = imageSrcList.indexOf(currentImg)
        const lastImgInList = imgIndex === imageSrcList.length-1
        const firstImgInList = imgIndex === 0
        let newImg = null
        if (isRightSwipe && !firstImgInList){
            newImg = imageSrcList[imgIndex-1]
            self.loadImage(newImg)
        } else if (!isRightSwipe && !lastImgInList) {
            newImg = imageSrcList[imgIndex+1]
            self.loadImage(newImg)
        }
        if(newImg) currentImg = newImg
    }

    saveImagesinList(event) {
        const imageList = Array.from(event.target.parentElement.parentElement.querySelectorAll('img'))
        imageSrcList = imageList.map(img => {
            return img.src
        })
    }


    openImageInPopup(event) {
        currentImg = event.target.src
        this.openModalForImage(event)
        this.saveImagesinList(event)

    }

    mappingFunction(object) {
        let self = this
        const result = {};
        for (const key in self.Mapping) {
            const newKey = self.Mapping[key];
            if (object.hasOwnProperty(key)) {
                result[newKey] = object[key];
            } else {
                result[newKey] = null;
            }
        }
        return result;
    }

    onTwoFingerDrag (event) {
        console.log("onTwoFingerDrag, event: ", event)
        if (event.type === 'touchstart' && event.touches.length === 1) {
            event.currentTarget.classList.add('swiping')
        } else {
            event.currentTarget.classList.remove('swiping')
        }
    }

    onScrollSlider(e) {
        let self = this
        self.highlightThumb(Math.floor(self.imageSliderContainerTarget.scrollLeft / self.imageSliderContainerTarget.offsetWidth))
    }

    selectImage(e) {
        let self = this
        self.imageSliderContainerTarget.scrollTo({left: (Number(e.params.imageIndex) - 1) * self.imageSliderContainerTarget.offsetWidth, top: 0})
        self.deselectThumbs(e.target.closest('ul'));
        e.target.closest('li').classList.add('selected');
    }

    highlightThumb(index) {
        let self = this
        self.deselectThumbs(self.thumbListTarget)
        self.thumbListTarget.getElementsByTagName('li')[index].classList.add('selected')
    }

    deselectThumbs(list) {
        for (const item of list.querySelectorAll('li')) {
            item.classList.remove('selected');
        }
    }

    loadImage(imgSrc) {
        while (imageContainer.firstChild) {
            imageContainer.removeChild(imageContainer.firstChild)
        }
        const image = document.createElement('img')
        image.classList.add('selectedImage')
        image.src = imgSrc
        imageContainer.appendChild(image)


        document.querySelectorAll(".container__image").forEach(element => {
            this.pinchZoom(element);
        });
    }

    openModalForImage(event) {
        let self = this
        modal = document.querySelector('.modal--transparent')
        modalBackdrop = document.querySelector('.modal-backdrop')
        imageContainer = document.querySelector('#container-image')

        self.loadImage(event.target.currentSrc)

        modal.classList.add('show')
        modalBackdrop.classList.add('show')
        document.body.classList.add('show-modal--transparent')
    }

    pinchZoom = (imageElement) => {
        let imageElementScale = 1;

        let start = {};

        // Calculate distance between two fingers
        const distance = (event) => {
            const dist = Math.hypot(event.touches[0].pageX - event.touches[1].pageX, event.touches[0].pageY - event.touches[1].pageY);
          return dist
        };

        imageElement.addEventListener('touchstart', (event) => {
            console.log('touchstart')
          if (event.touches.length === 2) {
            event.preventDefault(); // Prevent page scroll
            console.log('event.touches.length === 2')
            // Calculate where the fingers have started on the X and Y axis
            start.x = (event.touches[0].pageX + event.touches[1].pageX) / 2;
            start.y = (event.touches[0].pageY + event.touches[1].pageY) / 2;
            start.distance = distance(event);
          }
        });

        imageElement.addEventListener('touchmove', (event) => {
            console.log('touchmove')
          if (event.touches.length === 2) {
            console.log('event.touches.length === 2')
            event.preventDefault(); // Prevent page scroll

            // Safari provides event.scale as two fingers move on the screen
            // For other browsers just calculate the scale manually
            let scale;
            if (event.scale) {
              scale = event.scale;
            } else {
              const deltaDistance = distance(event);
              scale = deltaDistance / start.distance;
            }
            imageElementScale = Math.min(Math.max(1, scale), 4);

            // Calculate how much the fingers have moved on the X and Y axis
            const deltaX = (((event.touches[0].pageX + event.touches[1].pageX) / 2) - start.x) * 2; // x2 for accelarated movement
            const deltaY = (((event.touches[0].pageY + event.touches[1].pageY) / 2) - start.y) * 2; // x2 for accelarated movement

            // Transform the image to make it grow and move with fingers
            const transform = `translate3d(${deltaX}px, ${deltaY}px, 0) scale(${imageElementScale})`;
            imageElement.style.transform = transform;
            imageElement.style.WebkitTransform = transform;
            imageElement.style.zIndex = "9999";
          }
        });

        imageElement.addEventListener('touchend', (event) => {
            console.log('touchend')
          // Reset image to it's original format
          imageElement.style.transform = "";
          imageElement.style.WebkitTransform = "";
          imageElement.style.zIndex = "";
        });
      }
}
