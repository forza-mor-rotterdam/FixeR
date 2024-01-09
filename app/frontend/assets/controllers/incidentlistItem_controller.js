import { Controller } from '@hotwired/stimulus';

export default class extends Controller {

    initialize() {
        let observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.intersectionRatio > 0) {
                    const container = entry.target.querySelectorAll('.background-image')[0]
                    const imageSrc = container.getAttribute('data-src')
                    if(imageSrc){
                        container.style = imageSrc
                        container.removeAttribute('data-src');
                    }
                }
            })
        })
        observer.observe(this.element);
    }
}
