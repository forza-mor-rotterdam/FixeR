import { Controller } from '@hotwired/stimulus';


export default class extends Controller {
    static targets = [ "title", "subTitle", "turboFrame", "closeModalElement" ]

    initialize() {
        document.body.classList.remove('show-modal');
        console.log("modal init")

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
              this.closeModal()
            }
        })
    }
    closeModalElementTargetConnected(element){
        let self = this
        if (element.dataset.turboFrameId){
            let turboElement = document.getElementById(element.dataset.turboFrameId)
            turboElement.src = element.dataset.turboFrameSrc
            self.closeModal()
            turboElement.reload()
        }
    }
    closeModal(event) {
        let self = this
        const modal = self.element.querySelector('.modal');
        const modalBackdrop = self.element.querySelector('.modal-backdrop');
        if (self.hasTurboFrameTarget){
            self.turboFrameTarget.innerHTML = ""
        }
        modal.classList.remove('show');
        modalBackdrop.classList.remove('show');
        document.body.classList.remove('show-modal', 'show-modal--transparent');
    }
    openModal(event) {
        let self = this
        if (self.hasTitleTarget){
            self.titleTarget.innerHTML = event.params.title
        }
        if (self.hasSubTitleTarget){
            self.subTitleTarget.innerHTML = event.params.subTitle
        }
        let modal = this.element.querySelector('.modal')
        if (self.hasTurboFrameTarget){
            self.turboFrameTarget.id = event.params.id
            self.turboFrameTarget.src = event.params.url
            modal = self.turboFrameTarget.closest('.modal');
        }
        const modalBackdrop = modal.querySelector('.modal-backdrop');
        modal.classList.add('show');
        modalBackdrop.classList.add('show');
        document.body.classList.add('show-modal');
    }
}
