import { Controller } from '@hotwired/stimulus';

export default class extends Controller {
    static targets = ["button"]
    connect() {
        
        const frame = this.rootTarget.closest("turbo-frame")
        const swiper = this.rootTarget.querySelector('.wrapper__swipe')
        console.log('swiper', swiper)
        let initialTouchPos = null
        if (this.isSubmittedValue == "True"){
            setTimeout(function (){
                frame.reload()
            }, 4000)
        }

        // Check if pointer events are supported.
        
        if (window.PointerEvent) {
            // Add Pointer Event Listener
            console.log('haai', swiper)
            this.rootTarget.querySelector('.wrapper__swipe').addEventListener('pointerdown', this.handleGestureStart.bind(this), true);
            this.rootTarget.querySelector('.wrapper__swipe').addEventListener('pointermove', this.handleGestureMove.bind(this), true);
            this.rootTarget.querySelector('.wrapper__swipe').addEventListener('pointerup', this.handleGestureEnd.bind(this), true);
            this.rootTarget.querySelector('.wrapper__swipe').addEventListener('pointercancel', this.handleGestureEnd.bind(this), true);
        } else {
            // Add Touch Listener
            this.rootTarget.querySelector('.wrapper__swipe').addEventListener('touchstart', this.handleGestureStart, true);
            this.rootTarget.querySelector('.wrapper__swipe').addEventListener('touchmove', this.handleGestureMove, true);
            this.rootTarget.querySelector('.wrapper__swipe').addEventListener('touchend', this.handleGestureEnd, true);
            this.rootTarget.querySelector('.wrapper__swipe').addEventListener('touchcancel', this.handleGestureEnd, true);
        
            // Add Mouse Listener
            this.rootTarget.querySelector('.wrapper__swipe').addEventListener('mousedown', this.handleGestureStart, true);
        }

    }

    formHandleIsConnectedHandler(event) {
        const removeElem = this.element.parentNode;
        if (event.detail.is_handled){
            this.element.classList.add("hide");
            this.element.addEventListener('transitionend', function(e){
                removeElem.parentNode.removeChild(removeElem);
            });
            const btn = this.element.querySelector("button");
            console.log(btn)
            this.buttonTarget.textContent = event.detail.messages.join(",")
        }
    }

    // Handle the start of gestures
    handleGestureStart(evt) {
        evt.preventDefault();
       
        if(evt.touches && evt.touches.length > 1) {
            return;
        }
    
        // Add the move and end listeners
        if (window.PointerEvent) {
            evt.target.setPointerCapture(evt.pointerId);
            console.log('PointerEvent')
        } else {
            // Add Mouse Listeners
            console.log('Mouse Listeners')

            document.addEventListener('mousemove', this.handleGestureMove, true);
            document.addEventListener('mouseup', this.handleGestureEnd, true);
        }
    
        this.initialTouchPos = this.getGesturePointFromEvent(evt);
    
    
        // console.log('swipert', swiper)
        console.log('this.swipert', this.rootTarget.querySelector('.wrapper__swipe'))
        this.rootTarget.querySelector('.wrapper__swipe').style.transition = 'initial';
    }

    // Handle end gestures
    handleGestureEnd(evt) {
        evt.preventDefault();
    
        if (evt.touches && evt.touches.length > 0) {
            return;
        }
    
        // this.rafPending = false;
    
        // Remove Event Listeners
        if (window.PointerEvent) {
            evt.target.releasePointerCapture(evt.pointerId);
        } else {
            // Remove Mouse Listeners
            document.removeEventListener('mousemove', this.handleGestureMove, true);
            document.removeEventListener('mouseup', this.handleGestureEnd, true);
        }
    
        // updateSwipeRestPosition();
    
        this.initialTouchPos = null;
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

    handleGestureMove(evt) {
        evt.preventDefault();
        // console.log('handleGestureMove 1', this.rafPending)
      
        if (!this.initialTouchPos) {
          return;
        }
      
        this.lastTouchPos = this.getGesturePointFromEvent(evt);
      
        // if (this.rafPending) {
        //   return;
        // }
      
        // this.rafPending = true;
      
        // console.log('handleGestureMove 2', this.rafPending)

        // window.requestAnimationFrame(this.onAnimFrame);
        this.onAnimFrame()
    }

    onAnimFrame() {
        console.log('onAnimFrame')
        
        // if (!this.rafPending) {
        //     console.log('return')
        //   return;
        // }
      
        var differenceInX = this.initialTouchPos.x - this.lastTouchPos.x;
        var newXTransform = (0 - differenceInX)+'px';
        var transformStyle = 'translateX('+newXTransform+')';
      
        this.rootTarget.querySelector('.wrapper__swipe').style.webkitTransform = transformStyle;
        this.rootTarget.querySelector('.wrapper__swipe').style.MozTransform = transformStyle;
        this.rootTarget.querySelector('.wrapper__swipe').style.msTransform = transformStyle;
        this.rootTarget.querySelector('.wrapper__swipe').style.transform = transformStyle;
      
        this.rafPending = false;
        console.log('onAnimFrame, transformStyle', transformStyle)
        
    }

    swipe(e) {
        // const li = e.target.tagName.toLowerCase() !== "img" && e.target.closest("li");
        // const btn = e.target.closest("button");
        // const anchor = e.target.closest("div.background-image")
        // if(!anchor){
        //     if (li && li.scrollLeft === 0) {
        //         li.scrollBy({
        //         left: 1,
        //         behavior: "smooth"
        //         });
        //     } else if (!btn && li) {
        //         li.scrollBy({
        //         left: -1,
        //         behavior: "smooth"
        //         });
        //     } else if (btn && li) {
        //         // window.location.href=`/incident/${this.idValue}/handle`;
        //         li.scrollBy({
        //             left: -1,
        //             behavior: "smooth"
        //         });
        //     }
        // }
    }

    openModal(e) {
        const data = e.params.object;
        const modal = this.element.querySelector('.modal');
        const modalBackdrop = this.element.querySelector('.modal-backdrop');

        modal.setAttribute('data-id', data.id);
        modal.setAttribute('data-subjectId', data.onderwerp.id);
        
        modal.classList.add('show');
        modalBackdrop.classList.add('show');
        document.body.classList.add('show-modal');
        const exits = modal.querySelectorAll('.modal-exit');
        exits.forEach(function (exit) {
            exit.addEventListener('click', function (event) {
                event.preventDefault();
                modal.classList.remove('show');
                modalBackdrop.classList.remove('show');
                document.body.classList.remove('show-modal');
            });
        });
    }
}
