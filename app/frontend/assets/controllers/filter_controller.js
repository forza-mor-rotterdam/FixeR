import { Controller } from '@hotwired/stimulus';

export default class extends Controller {
    static targets = [ "foldoutStatesField", "filterInput" ]

    showFilters() {
        document.body.classList.add('show-filters')
    }

    hideFilters() {
        const frame = document.getElementById('taken_lijst');
        frame.reload()
        document.body.classList.remove('show-filters')
    }

    removeFilter(e) {
        const input = document.querySelector(`[name="${e.params.description}"][value="${e.params.code}"]`);
        input.checked = false;
        this.element.requestSubmit()
    }
    toggleActiveFilter(e) {
        e.preventDefault()
        const input = this.foldoutStatesFieldTarget;
        let idArray = JSON.parse(input.value)
        const idAttr = e.target.getAttribute("id")
        const isOpen = e.target.hasAttribute("open")
        let index = idArray.indexOf(idAttr)
        if (index > -1) {
            idArray.splice(index, 1);
        }
        if (isOpen){
            idArray.push(idAttr);
        }
        input.value = JSON.stringify(idArray)
    }

    onChangeFilter() {
        this.element.requestSubmit()
    }

    onSubmitFilter() {
        this.hideFilters()
    }

    selectAll(e) {
        const checkList = Array.from(e.target.closest('details').querySelectorAll('.form-check-input'))
        const doCheck = e.params.filterType === 'all'
        checkList.forEach(element => {
            element.checked = doCheck
        });
    }

    removeAllFilters(e) {
        this.filterInputTargets.checked = false
        this.filterInputTargets.forEach(input => {
            input.checked = false;
        })
        this.element.requestSubmit()
    }
}
