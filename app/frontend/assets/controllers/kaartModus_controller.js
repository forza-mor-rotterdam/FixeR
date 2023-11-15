import { Controller } from '@hotwired/stimulus';

export default class extends Controller {

    static targets = [ "form" ]

    connect() {
        const field = this.formTarget.querySelector("[name='kaart_modus']:checked")
        let kaartModusChangeEvent = new CustomEvent('kaartModusChangeEvent', { bubbles: true, cancelable: false, detail: {kaartModus:field.value}});
        this.element.dispatchEvent(kaartModusChangeEvent);
        field.parentNode.classList.add("active")
    }
    onChangeHandler(e){
        // console.log("onChangeHandler", e)
    }
    kaartModusOptionClickHandler(e){
        this.formTarget.requestSubmit()
    }
}
