import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['log']
  connect() {
    this.originalLogPrefix = 'org'
    this.fixLoggingFunc('log')
    this.fixLoggingFunc('debug')
    this.fixLoggingFunc('warn')
    this.fixLoggingFunc('error')
    this.fixLoggingFunc('info')
  }
  fixLoggingFunc(name) {
    if (!console[this.originalLogPrefix + name]) {
      console[this.originalLogPrefix + name] = console[name]
      if (this.hasLogTarget) {
        console[name] = (...args) => {
          const output = this.produceOutput(name, args)
          this.logTarget.insertBefore(output, this.logTarget.firstChild)
          if (this.logTarget.children.length > 100) {
            this.logTarget.removeChild(this.logTarget.lastChild)
          }
          console[this.originalLogPrefix + name].apply(undefined, args)
        }
      }
    }
  }
  stringify(arg) {
    try {
      if (arg && arg.outerHTML) {
        return `${arg.outerHTML.replace(arg.innerHTML, '...')}`
      }
      return typeof arg === 'object' && (JSON || {}).stringify ? JSON.stringify(arg) : arg
    } catch (e) {
      return `errr: ${e}`
    }
  }
  produceOutput(name, args) {
    const spanContainer = document.createElement('SPAN')
    const hr = document.createElement('HR')
    args?.map((arg) => {
      const span = document.createElement('SPAN')
      span.classList.add('log', `log-${name}`, `log-${typeof arg}`)
      span.textContent = this.stringify(arg)
      spanContainer.appendChild(span)
    })
    spanContainer.appendChild(hr)
    return spanContainer
  }
}
