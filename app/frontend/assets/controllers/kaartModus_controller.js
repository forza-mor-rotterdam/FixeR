import { Controller } from '@hotwired/stimulus';

export default class extends Controller {

    static targets = [ "form" ]

    connect() {}

    onChangeHandler(e){
        this.formTarget.requestSubmit()
    }
    kaartModusOptionClickHandler(e){
        let kaartModusChangeEvent = new CustomEvent('kaartModusChangeEvent', { bubbles: true, cancelable: false, detail: {kaartModus:e.target.value}});
        this.element.dispatchEvent(kaartModusChangeEvent);
    }
}
