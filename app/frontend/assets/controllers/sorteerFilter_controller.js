import { Controller } from '@hotwired/stimulus';

export default class extends Controller {

    static targets = [ "form", "sorteerField"]

    connect() {
        let orderChangeEvent = new CustomEvent('orderChangeEvent', { bubbles: true, cancelable: false, detail: {order:this.sorteerFieldTarget.value}});
        this.element.dispatchEvent(orderChangeEvent);
    }
    onChangeHandler(e){
        this.formTarget.requestSubmit()
    }
}
