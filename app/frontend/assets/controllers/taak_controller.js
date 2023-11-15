import { Controller } from '@hotwired/stimulus';

let self = null
export default class extends Controller {
    static targets = ["turboFormHandler", "incidentDate"]
    static values = {
        date: String,
        days: String
    }

    initialize() {
        self = this
        self.element[self.identifier] = self
    }

    connect() {
        if(this.element.classList.contains('list-item')) {
            this.initialTouchPos = null
            this.bindStart = this.handleGestureStart.bind(this);
            this.bindMove = this.handleGestureMove.bind(this);
            this.bindEnd = this.handleGestureEnd.bind(this);
            this.addInitialListeners();
            this.isMoving = false;

            if(!!this.dateValue && !!this.daysValue) {
                this.incidentDateTarget.textContent = this.getNumberOfDays(this.dateValue, parseInt(this.daysValue))
            }
        }

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
              this.closeModal()
            }
        })
    }

    disconnect() {
        this.removeAllListeners()
    }

    selectTaak(e) {
        this.element.dispatchEvent(new CustomEvent("taakIsSelected", {detail: {url:e.params.url, id:e.params.id}, bubbles: true}));
    }

    getNumberOfDays(date, days) {
        const date_incident = new Date(date);
        const dateTypes = ["Vandaag", "Gisteren", "Eergisteren", "dagen"]
        if(days < 3) {
            const minutes = date_incident.getMinutes() < 10 ? `0${date_incident.getMinutes()}` : date_incident.getMinutes();
            const time = `${date_incident.getHours()}:${minutes}`
            return `${dateTypes[1]}, ${time}`;
        } else {
            return `${days} werkdagen`
        }
    }

    addInitialListeners() {
        // Safari on iOS does not apply the active state by default
        if (/iP(hone|ad)/.test(window.navigator.userAgent)) {
            document.body.addEventListener('touchstart', function() {}, false);
        }
        if (window.PointerEvent) {
            // Add Pointer Event Listener
            this.element.addEventListener('pointerdown', this.bindStart, false);
        } else {
            // Add Touch Listener
            this.element.addEventListener('touchstart', this.bindStart, false);
            // Add Mouse Listener
            this.element.addEventListener('mousedown', this.bindStart, false);
        }
    }

    addAllListeners() {
         // Check if pointer events are supported.
         if (window.PointerEvent) {
            // Add Pointer Event Listener
            this.element.addEventListener('pointerdown', this.bindStart, false);
            this.element.addEventListener('pointermove', this.bindMove, false);
            this.element.addEventListener('pointerup', this.bindEnd, false);
            this.element.addEventListener('pointercancel', this.bindEnd, false);
        } else {
            // Add Touch Listener
            this.element.addEventListener('touchstart', this.bindStart, false);
            this.element.addEventListener('touchmove', this.bindMove, false);
            this.element.addEventListener('touchend', this.bindEnd, false);
            this.element.addEventListener('touchcancel', this.bindEnd, false);
            // Add Mouse Listener
            this.element.addEventListener('mousedown', this.bindStart, false);
        }
    }

    removeAllListeners() {
        // Check if pointer events are supported.
        if (window.PointerEvent) {
           // Add Pointer Event Listener
           this.element.removeEventListener('pointerdown', this.bindStart, false);
           this.element.removeEventListener('pointermove', this.bindMove, false);
           this.element.removeEventListener('pointerup', this.bindEnd, false);
           this.element.removeEventListener('pointercancel', this.bindEnd, false);
       } else {
           // Add Touch Listener
           this.element.removeEventListener('touchstart', this.bindStart, false);
           this.element.removeEventListener('touchmove', this.bindMove, false);
           this.element.removeEventListener('touchend', this.bindEnd, false);
           this.element.removeEventListener('touchcancel', this.bindEnd, false);
           // Add Mouse Listener
           this.element.removeEventListener('mousedown', this.bindStart, false);
       }
   }

    formHandleIsConnectedHandler(event) {
        const removeElem = this.element.parentNode;

        const frame = document.getElementById('incident_detail_part');
        frame?.reload()

        if (event.detail.is_handled){
            this.element.classList.add("hide");
            if(event.detail.handled_type) {
                this.showAlert(event.detail.handled_type)
            }
            this.element.addEventListener('transitionend', function(e){
                removeElem.parentNode?.removeChild(removeElem);
            });
            this.buttonTarget.textContent = event.detail.messages.join(",")
        }
    }

    showAlert(type) {
        const div = document.createElement('div')
        div.classList.add('message')
        if (type === "handled") {
            div.append("De melding is afgehandeld")
        } else {
            div.append("De melding is doorverwezen")
        }
        this.element.append(div)
    }

    cancelHandleHandler(event) {
        this.closeModal()
    }

    // Handle the start of gestures
    handleGestureStart(evt) {
        evt.preventDefault();
        this.isMoving = false;
        if((evt.touches && evt.touches.length > 1)) {
            return;
        }

        this.addAllListeners()
        this.initialTouchPos = this.getGesturePointFromEvent(evt);
    }

    // Handle end gestures
    handleGestureEnd(evt) {

        evt.preventDefault();
        if ((evt.touches && evt.touches.length > 0)) {
            return;
        }

        // this.removeAllListeners()
        this.updateSwipeRestPosition(evt);

        this.initialTouchPos = null;
        if (this.isMoving !== true) {
            this.isMoving = false;
        }
    }

    handleGestureMove(evt) {
        evt.preventDefault();
        this.isMoving = true;
        if (!this.initialTouchPos) {
          return;
        }

        this.lastTouchPos = this.getGesturePointFromEvent(evt);
        this.onAnimFrame()
    }

    getGesturePointFromEvent = function (evt) {
        var point = {};

        if (evt.targetTouches) {
          // Prefer Touch Events
          point.x = evt.targetTouches[0].clientX;
          point.y = evt.targetTouches[0].clientY;
        } else {
          // Either Mouse event or Pointer Event
          point.x = evt.clientX;
          point.y = evt.clientY;
        }

        return point;
    }

    onAnimFrame() {

        let differenceInX = this.initialTouchPos.x - this.lastTouchPos.x;
        let newLeft = (0 - differenceInX)+'px';
        let leftStyle = newLeft;

        if(differenceInX > -100 && differenceInX < 100) {
            this.element.style.left = leftStyle;
        } else if (differenceInX <= -100) {
            this.element.style.left = '100%';
            setTimeout(function (){
                this.openModal(false)
            }.bind(this), 500)


        } else {
            this.element.style.left = '-100%';
            setTimeout(function (){
                this.openModal(true)
            }.bind(this), 500)
        }
    }

    resetIncidentSwipe() {
        this.element.style.left = '0';
    }

    updateSwipeRestPosition(evt) {
        if(this.lastTouchPos) {
            let differenceInX = this.initialTouchPos.x - this.lastTouchPos.x;
            if(differenceInX > -100 && differenceInX < 100) {
                this.element.style.left = '0';
            }
            this.initialTouchPos = this.getGesturePointFromEvent(evt);
        }
    }

    closeModal() {
        const modal = this.element.querySelector('.modal');
        const modalBackdrop = this.element.querySelector('.modal-backdrop');
        modal.classList.remove('show');
        modalBackdrop.classList.remove('show');
        document.body.classList.remove('show-modal');
        this.addInitialListeners()
        this.turboFormHandlerTarget.innerHTML = ""
    }

    openModal(event) {
        let isFinished = true
        if (typeof(event) === 'boolean' ){
            isFinished = event
        } else if( typeof(event) === 'object' && event.params.isFinished) {
            isFinished = event.params.isFinished
        }

        this.turboFormHandlerTarget.setAttribute("src", this.turboFormHandlerTarget.dataset.src + (isFinished ? "?resolutie=opgelost": "?resolutie=niet_opgelost"))

        this.removeAllListeners()
        const modal = this.element.querySelector('.modal');
        const modalBackdrop = this.element.querySelector('.modal-backdrop');

        modal.classList.add('show');
        modalBackdrop.classList.add('show');
        document.body.classList.add('show-modal');

        // TODO only used for modal backdrop, try to get rid of it
        const exits = modal.querySelectorAll('.modal-exit');
        exits.forEach((exit) => {
            exit.addEventListener('click', (event) => {
                event.preventDefault();
                this.closeModal()
            });
        });

        setTimeout(function (){
            this.resetIncidentSwipe()
        }.bind(this), 1000)
    }
}
