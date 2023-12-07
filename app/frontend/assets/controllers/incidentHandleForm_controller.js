import { Controller } from '@hotwired/stimulus';

let form = null
let inputList = null
let input = null
let error = null
let defaultLabelInternalText = ""
const requiredLabelInternalText = "Waarom kan de taak niet worden afgerond?"
const defaultErrorMessage = "Vul a.u.b. dit veld in."
export default class extends Controller {
    static values = {
        formIsSubmitted: Boolean,
        parentContext: String,
        handledOptions: String,
    }

    static targets = ["externalText", "internalText", "newTask"]

    connect() {

        form = document.querySelector("form");
        inputList = document.querySelectorAll('[type="radio"]')
        // console.log("inputList", inputList)

        const btn = inputList.filter()

        for (let i=0; i<inputList.length; i++){
            input = inputList[i]
            console.log(input.checked)
            error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]

            input.addEventListener("input", (event) => {
                input.closest('.form-row').classList.remove('is-invalid')
                error.textContent = "";
            })
        };

        if(this.hasInternalTextTarget) {
            defaultLabelInternalText = this.internalTextTarget.querySelector('label').textContent
        }
    }

    doResolution(event) {
        if (event.target.value === "niet_opgelost") {
            if(this.hasInternalTextTarget) {
                this.internalTextTarget.querySelector('label').textContent = requiredLabelInternalText
                this.internalTextTarget.querySelector('textarea').setAttribute("required", true)
                this.internalTextTarget.closest(".wrapper--flex-order").style.flexDirection='column-reverse'
            }
        }else {
            if(this.hasInternalTextTarget) {
                this.internalTextTarget.querySelector('label').textContent = defaultLabelInternalText
                this.internalTextTarget.querySelector('textarea').removeAttribute("required")
                this.internalTextTarget.closest(".wrapper--flex-order").style.flexDirection='column'
            }
        }
    }
}
