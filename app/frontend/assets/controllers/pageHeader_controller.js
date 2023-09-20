import { Controller } from '@hotwired/stimulus';

export default class extends Controller {
    static targets = ["todo", "finished"]

    connect() {
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
              this.closeModal()
            }
        })
    }

    resetFontSize(e) {
        document.body.classList.remove('fz-medium', 'fz-large', 'fz-xlarge')
    }

    setFontSize(e) {
        const size = e.params.size;
        if(size) {
            this.resetFontSize()
            document.body.classList.add(size)
        }
    }

    openModal(e) {
        const currentUrl = window.location.href

        if (currentUrl.includes("/taken/")) {
            this.todoTarget.classList.add("selected")
        }
        if (currentUrl.includes("/taken-afgerond/")) {
            this.finishedTarget.classList.add("selected")
        }

        const modal = this.element.querySelector('.modal');
        const modalBackdrop = this.element.querySelector('.modal-backdrop');

        modal.classList.add('show');
        modalBackdrop.classList.add('show');
        document.body.classList.add('show-modal');
    }

    closeModal() {
        const modal = this.element.querySelector('.modal');
        const modalBackdrop = this.element.querySelector('.modal-backdrop');
        modal.classList.remove('show');
        modalBackdrop.classList.remove('show');
        document.body.classList.remove('show-modal');
    }
}
