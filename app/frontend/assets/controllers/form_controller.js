import { Controller } from '@hotwired/stimulus';

let selectOptions = null

export default class extends Controller {

    static targets = [ "searchSelect" ]

    initialize() {
        let self = this
        selectOptions = []
        if (self.hasSearchSelectTarget){
            const options = self.searchSelectTarget.querySelectorAll("option")
            for(let i = 0; i < options.length; i++){
                selectOptions.push({value: options[i].value, label: options[i].textContent})
            }
        }
    }

    connect() {}
    searchFieldChange(e){
        let self = this
        if (!self.hasSearchSelectTarget){
            return
        }
        self.searchSelectTarget.innerHTML = ''
        for(let i = 0; i < selectOptions.length; i++){
            const re = new RegExp(e.target.value, "gi");
            let option = document.createElement("option")
            if (re.test(selectOptions[i].label)){
                // let newContent = selectOptions[i].label
                option.value = selectOptions[i].value
                option.textContent = selectOptions[i].label
                // option.innerHTML = newContent.replace(re, function(match) {
                //     return "<mark style='color:red;'>" + match + "</mark>";
                // })
                self.searchSelectTarget.appendChild(option)
            }
        }
    }
}
