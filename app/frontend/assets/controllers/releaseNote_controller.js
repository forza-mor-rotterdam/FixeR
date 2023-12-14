import { Controller } from '@hotwired/stimulus';

let currentImg, imageContainer, modal, modalBackdrop = null
let imageSrcList = []

let self = null
export default class extends Controller {
    static values = {
        areaList: String,
        incidentObject: Object,
    }
    static targets = ['selectedImage', 'thumbList', 'imageSliderContainer']

    Mapping = {
        'fotos': 'media',
    };

    initialize() {
        let self = this
        if(self.hasThumbListTarget) {
            self.thumbListTarget.getElementsByTagName('li')[0].classList.add('selected')
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
    isValidHttpUrl(string) {
        let url;

        try {
          url = new URL(string);
        } catch (_) {
          return false;
        }

        return url.protocol === "http:" || url.protocol === "https:";
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
