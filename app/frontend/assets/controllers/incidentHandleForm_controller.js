import { Controller } from '@hotwired/stimulus';

let form = null
let inputList = null
let input = null
let error = null
const defaultErrorMessage = "Vul a.u.b. dit veld in."
export default class extends Controller {
    static values = {
        formIsSubmitted: Boolean,
        parentContext: String,
        handledOptions: String,
    }

    static targets = ["externalText", "internalText"]

    connect() {

        form = document.querySelector("form");
        inputList = document.querySelectorAll('[type="radio"]')

        for (let i=0; i<inputList.length; i++){
            input = inputList[i]
            error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]

            input.addEventListener("input", (event) => {
                console.log("input", input)
                input.closest('.form-row').classList.remove('is-invalid')
                error.textContent = "";
            })
        };
    }

    onSubmit(event) {
        const allFieldsValid = this.checkValids()

        if(!(allFieldsValid)){
            event.preventDefault();
            
        } else {
            form.requestSubmit()
        }
    }

    checkValids() {
        //check all radoofields for validity
        // if 1 or more fields is invalid, don't send the form (return false)
        inputList = document.querySelectorAll('[type="radio"]')
        let count = 0
        
        for (let i=0; i<inputList.length; i++){
            input = inputList[i]
            error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]
            
            if (input.checked === true) {
                count++
            }
        }
        if (count > 0) {
            input.closest('.form-row').classList.remove("is-invalid")
            error.textContent = ""
            return true
        }else {
            error.textContent = defaultErrorMessage
            input.closest('.form-row').classList.add("is-invalid")
            return false
        }
    }

    cancelHandle() {
        this.element.dispatchEvent(new CustomEvent("cancelHandle", {
            detail: JSON.parse(this.parentContextValue),
            bubbles: true
        }));
    }

    setExternalMessage(evt){
        this.choice =  evt.params.index
        this.externalMessage = JSON.parse(this.handledOptionsValue)[this.choice][2]
        this.externalTextTarget.value = this.externalMessage
    }

    defaultExternalMessage(){
        if(this.externalMessage.length === 0) return

        this.externalTextTarget.value = this.externalMessage
    }

    clearExternalMessage() {
        this.externalTextTarget.value = ""
    }
}
