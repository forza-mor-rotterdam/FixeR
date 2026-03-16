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
	const maxContentOffset = 96
	let startY = 0
	let pullDistance = 0
	let isTracking = false

	const indicator = document.createElement('div')
	indicator.className = 'pull-to-refresh-indicator'
	indicator.innerHTML =
		'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="8 15 12 19 16 15"></polyline></svg>'
	document.body.prepend(indicator)
	const pullTargets = Array.from(document.body.children).filter(
		(element) => element !== indicator
	)

	function updateContentOffset(distance) {
		const offset = Math.min(distance * 0.6, maxContentOffset)

		pullTargets.forEach((element) => {
			element.style.transition = 'none'
			element.style.transform = `translateY(${offset}px)`
		})
	}

	function resetContentOffset() {
		pullTargets.forEach((element) => {
			element.style.transition = 'transform 0.3s ease'
			element.style.transform = ''
		})
	}

	function updateIndicator(distance) {
		indicator.classList.remove('is-hiding')
		const progress = Math.min(distance / refreshThreshold, 1)
		const yOffset = -52 + progress * 60
		indicator.style.transform = `translate(-50%, ${yOffset}px)`
		indicator.style.opacity = String(progress)
		indicator.classList.toggle('is-ready', distance >= refreshThreshold)
	}

	function hideIndicator() {
		indicator.classList.add('is-hiding')
		indicator.classList.remove('is-ready')
		indicator.style.transform = 'translate(-50%, -52px)'
		indicator.style.opacity = '0'
		resetContentOffset()
	}

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
				updateContentOffset(pullDistance)
				updateIndicator(pullDistance)
			}
		},
		{ passive: false }
	)

	window.addEventListener('touchend', () => {
		if (!isTracking) {
			return
		}

		isTracking = false
		resetContentOffset()
		if (pullDistance >= refreshThreshold) {
			window.location.reload()
		} else {
			hideIndicator()
		}
		pullDistance = 0
	})
}

function initDomFeatures() {
	initPullToRefresh()
}

const application = StimulusApplication.start()
const context = require.context('./controllers', true, /\.js$/)
application.load(definitionsFromContext(context))
console.log('git hash: ' + GITHUB_SHA)
window.Stimulus = application

TurboStart()

if (document.body) {
	initDomFeatures()
} else {
	document.addEventListener('DOMContentLoaded', initDomFeatures, { once: true })
}
