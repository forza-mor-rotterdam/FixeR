import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['log']
  initialize() {
    this.fixLoggingFunc('log')
    this.fixLoggingFunc('debug')
    this.fixLoggingFunc('warn')
    this.fixLoggingFunc('error')
    this.fixLoggingFunc('info')
  }
  fixLoggingFunc(name) {
    console['old' + name] = console[name]
    console[name] = (...args) => {
      const output = this.produceOutput(name, args)
      const eleLog = this.logTarget
      eleLog.insertBefore(output, eleLog.firstChild)
      console['old' + name].apply(undefined, args)
    }
  }
  stringify(arg) {
    if (arg && arg.outerHTML) {
      return `${arg.outerHTML.replace(arg.innerHTML, '...')}`
    }
    return typeof arg === 'object' && (JSON || {}).stringify ? JSON.stringify(arg) : arg
  }
  produceOutput(name, args) {
    const spanContainer = document.createElement('SPAN')
    const hr = document.createElement('HR')
    args.map((arg) => {
      const span = document.createElement('SPAN')
      span.classList.add('log', `log-${typeof arg}-${name}`)
      span.textContent = this.stringify(arg)
      spanContainer.appendChild(span)
    })
    spanContainer.appendChild(hr)
    return spanContainer
  }
}
