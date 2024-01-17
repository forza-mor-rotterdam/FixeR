import { Controller } from '@hotwired/stimulus';

let form = null
let inputList = null
let input = null
let error = null
let defaultLabelInternalText = ""
const requiredLabelInternalText = "Waarom kan de taak niet worden afgerond?"
const defaultErrorMessage = "Vul a.u.b. dit veld in."
export default class extends Controller {

    static targets = ["externalText", "internalText", "newTask"]

    connect() {

        form = document.querySelector("form");
        inputList = Array.from(document.querySelectorAll('[type="radio"]'))

        const btn = inputList.find((input) => {
            input.value == "niet_opgelost"
        })

        for (let i=0; i<inputList.length; i++){
            input = inputList[i]
            error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]

            input.addEventListener("input", (event) => {
                input.closest('.form-row').classList.remove('is-invalid')
                error.textContent = "";
            })

            if(input.value === "niet_opgelost" && input.checked === true) {
                console.log("NIET OPGELOST")
                this.onResolutionFalse()
            }
        };

        if(this.hasInternalTextTarget) {
            defaultLabelInternalText = this.internalTextTarget.querySelector('label').textContent
        }
    }

    onResolutionFalse() {
        if(this.hasInternalTextTarget) {
            this.internalTextTarget.querySelector('label').textContent = requiredLabelInternalText
            this.internalTextTarget.querySelector('textarea').setAttribute("required", true)
            this.internalTextTarget.closest(".wrapper--flex-order").style.flexDirection='column-reverse'
        }
    }

    onResolutionTrue() {
        if(this.hasInternalTextTarget) {
            this.internalTextTarget.querySelector('label').textContent = defaultLabelInternalText
            this.internalTextTarget.querySelector('textarea').removeAttribute("required")
            this.internalTextTarget.closest(".wrapper--flex-order").style.flexDirection='column'
        }
    }

    onChangeResolution(event) {
        if (event.target.value === "niet_opgelost") {
            this.onResolutionFalse()
       }else {
            this.onResolutionTrue()
        }
    }

    checkValids() {
        inputList = document.querySelectorAll('textarea[required]')
        let count = 0

        if(inputList.length > 0) {
            for (let i=0; i<inputList.length; i++){
                input = inputList[i]
                error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]
                if (input.value.length > 0) {
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
        } else {
            return true
        }

    }

    onSubmit(event) {
        const allFieldsValid = this.checkValids()
        if(!(allFieldsValid)){
            event.preventDefault();
        } else {
            form.requestSubmit()
        }
    }
}
