import { Controller } from '@hotwired/stimulus';

let observer = null
export default class extends Controller {

    initialize() {
        observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const container = entry.target.querySelectorAll('.background-image img')[0]
                    const imageSrc = container.getAttribute('data-src')
                    if(imageSrc){
                        container.src = imageSrc
                        container.removeAttribute('data-src');
                    }
                }
            })
        })
        observer.observe(this.element);
    }

    disconnect() {
        observer.disconnect();
    }
}
