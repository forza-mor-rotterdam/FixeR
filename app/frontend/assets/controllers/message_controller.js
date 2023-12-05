import { Controller } from '@hotwired/stimulus';


export default class extends Controller {
    static values = {
        mercurePublicUrl: String,
    }
    initialize() {
        let self = this
        self.initMessages()
    }
    initMessages(){
        let self = this
        if (self.hasMercurePublicUrlValue){
            const url = new URL(self.mercurePublicUrlValue);
            // subscribe with a topic like below
            // url.searchParams.append('topic', [messages topic]);

            self.eventSource = new EventSource(url);
            self.eventSource.onmessage = e => self.onMessage(e)
            self.eventSource.onerror = (e) => self.onMessageError(e)
        }
    }
    onMessage(e){
        let data  = JSON.parse(e.data)
        console.log(data)
    }
    onMessageError(e){
        let self = this
        console.log(e)
        console.log("An error occurred while attempting to connect.");
        self.eventSource.close()
    }
}
