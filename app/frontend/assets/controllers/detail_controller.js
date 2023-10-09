import { Controller } from '@hotwired/stimulus';

export default class extends Controller {
    static values = {
        incidentX: String,
        incidentY: String,
        areaList: String,
        currentDistrict: String,
        incidentObject: Object
    }
    static targets = ['selectedImage', 'thumbList', 'imageSliderContainer']

    Mapping = {
        'fotos': 'media',
    };

    initialize() {
        if(this.hasThumbListTarget) {
            this.thumbListTarget.getElementsByTagName('li')[0].classList.add('selected')
        }

        const incidentCoordinates = [parseFloat(this.incidentXValue.replace(/,/g, '.')), parseFloat(this.incidentYValue.replace(/,/g, '.'))]
        const map = L.map('incidentMap', {
            zoomControl: false,
            maxZoom: 18,
            minZoom: 13,
            dragging: false,
            tap: false
        }).setView(incidentCoordinates, 16);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        const marker = L.marker(incidentCoordinates).addTo(map);
    }

    mappingFunction(object) {
        const result = {};
        for (const key in this.Mapping) {
			const newKey = this.Mapping[key];
            if (object.hasOwnProperty(key)) {
                result[newKey] = object[key];
            } else {
                result[newKey] = null;
            }
        }
        return result;
    }

    onTwoFingerDrag (e) {
        if (e.type === 'touchstart' && e.touches.length === 1) {
            e.currentTarget.classList.add('swiping')
        } else {
            e.currentTarget.classList.remove('swiping')
        }
    }

    onScrollSlider(e) {
        this.highlightThumb(Math.floor(this.imageSliderContainerTarget.scrollLeft / this.imageSliderContainerTarget.offsetWidth))
    }

    selectImage(e) {
        this.imageSliderContainerTarget.scrollTo({left: (Number(e.params.imageIndex) - 1) * this.imageSliderContainerTarget.offsetWidth, top: 0})
        this.deselectThumbs(e.target.closest('ul'));
        e.target.closest('li').classList.add('selected');
    }

    highlightThumb(index) {
        this.deselectThumbs(this.thumbListTarget)
        this.thumbListTarget.getElementsByTagName('li')[index].classList.add('selected')
    }

    deselectThumbs(list) {
        for (const item of list.querySelectorAll('li')) {
            item.classList.remove('selected');
        }
    }
}
