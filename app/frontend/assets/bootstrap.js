import { Application as StimulusApplication } from '@hotwired/stimulus'
import { start as TurboStart } from '@hotwired/turbo'
import { definitionsFromContext } from '@hotwired/stimulus-webpack-helpers'
import { GITHUB_SHA } from './constants/environment'

function isStandaloneDisplayMode() {
	return (
		window.matchMedia('(display-mode: standalone)').matches ||
		window.navigator.standalone === true
	)
}

function initPullToRefresh() {
	if (!isStandaloneDisplayMode()) {
		return
	}

	const refreshThreshold = 80
	let startY = 0
	let pullDistance = 0
	let isTracking = false

	window.addEventListener(
		'touchstart',
		(event) => {
			if (event.touches.length !== 1 || window.scrollY > 0) {
				isTracking = false
				return
			}

			if (document.body.classList.contains('show-dialog')) {
				isTracking = false
				return
			}

			startY = event.touches[0].clientY
			pullDistance = 0
			isTracking = true
		},
		{ passive: true }
	)

	window.addEventListener(
		'touchmove',
		(event) => {
			if (!isTracking) {
				return
			}

			const currentY = event.touches[0].clientY
			pullDistance = Math.max(0, currentY - startY)

			if (pullDistance > 0) {
				event.preventDefault()
			}
		},
		{ passive: false }
	)

	window.addEventListener('touchend', () => {
		if (!isTracking) {
			return
		}

		isTracking = false
		if (pullDistance >= refreshThreshold) {
			window.location.reload()
		}
		pullDistance = 0
	})
}

const application = StimulusApplication.start()
const context = require.context('./controllers', true, /\.js$/)
application.load(definitionsFromContext(context))
console.log('git hash: ' + GITHUB_SHA)
window.Stimulus = application

TurboStart()
initPullToRefresh()
