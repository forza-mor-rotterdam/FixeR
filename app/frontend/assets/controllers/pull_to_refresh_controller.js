import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
	connect() {
		if (!this.isStandaloneDisplayMode()) {
			return
		}

		this.initPullToRefresh()
	}

	isStandaloneDisplayMode() {
		return (
			window.matchMedia('(display-mode: standalone)').matches ||
			window.navigator.standalone === true
		)
	}

	initPullToRefresh() {
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

		const updateContentOffset = (distance) => {
			const offset = Math.min(distance * 0.6, maxContentOffset)

			pullTargets.forEach((element) => {
				element.style.transition = 'none'
				element.style.transform = `translateY(${offset}px)`
			})
		}

		const resetContentOffset = () => {
			pullTargets.forEach((element) => {
				element.style.transition = 'transform 0.3s ease'
				element.style.transform = ''
			})
		}

		const updateIndicator = (distance) => {
			indicator.classList.remove('is-hiding')
			const progress = Math.min(distance / refreshThreshold, 1)
			const yOffset = -52 + progress * 60
			indicator.style.transform = `translate(-50%, ${yOffset}px)`
			indicator.style.opacity = String(progress)
			indicator.classList.toggle('is-ready', distance >= refreshThreshold)
		}

		const hideIndicator = () => {
			indicator.classList.add('is-hiding')
			indicator.classList.remove('is-ready')
			indicator.style.transform = 'translate(-50%, -52px)'
			indicator.style.opacity = '0'
			resetContentOffset()
		}

		const handleTouchStart = (event) => {
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
		}

		const handleTouchMove = (event) => {
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
		}

		const handleTouchEnd = () => {
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
		}

		window.addEventListener('touchstart', handleTouchStart, { passive: true })
		window.addEventListener('touchmove', handleTouchMove, { passive: false })
		window.addEventListener('touchend', handleTouchEnd)
	}
}
