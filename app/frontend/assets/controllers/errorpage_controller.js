import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['question', 'containerAnswers']
  connect() {
    const questions = [
      {
        question: `Da's als kakken zonder douwen`,
        choices: [
          'Iets wat makkelijk is',
          'Praten zonder te luisteren',
          'Ander woord voor "buikgriep"',
        ],
        correct: 0,
      },
      {
        question: 'What is the capital of United Kingdom?',
        choices: ['London', 'Paris', 'Nairobi'],
        correct: 0,
      },
      {
        question: 'How many days are there in a week?',
        choices: ['Five', 'Three', 'Seven'],
        correct: 2,
      },
      {
        question: 'What is the closest planet to the sun?',
        choices: ['Earth', 'Mercury', 'Saturn'],
        correct: 1,
      },
    ]
    const index = Math.floor(questions.length * Math.random())
    console.log('questions', index)
    this.questionTarget.textContent = questions[index].question

    for (let i = 0; i < questions[index].choices.length; i++) {
      let btn = document.createElement('button')
      btn.classList.add('btn')
      btn.textContent = questions[index].choices[i]
      btn.addEventListener('click', function () {
        if (i === questions[index].correct) {
          confettiLoop()
        }
      })
      this.containerAnswersTarget.appendChild(btn)
    }

    // start confetti
    // global variables
    const confetti = document.getElementById('confetti')
    const confettiCtx = confetti.getContext('2d')
    let container,
      confettiElements = [],
      clickPosition

    // helper
    const rand = (min, max) => Math.random() * (max - min) + min

    // params to play with
    const confettiParams = {
      // number of confetti per "explosion"
      number: 70,
      // min and max size for each rectangle
      size: { x: [5, 20], y: [10, 18] },
      // power of explosion
      initSpeed: 25,
      // defines how fast particles go down after blast-off
      gravity: 0.65,
      // how wide is explosion
      drag: 0.08,
      // how slow particles are falling
      terminalVelocity: 6,
      // how fast particles are rotating around themselves
      flipSpeed: 0.017,
    }
    const colors = [
      { front: '#00811f', back: '#006e32' },
      { front: '#c93675', back: '#a12b5e' },
      { front: '#00811f', back: '#006e32' },
      { front: '#c93675', back: '#a12b5e' },
      { front: '#00811f', back: '#006e32' },
      { front: '#c93675', back: '#a12b5e' },
      { front: '#00811f', back: '#006e32' },
      { front: '#c93675', back: '#a12b5e' },
      { front: '#ffc107', back: '#fd7e14' },
      { front: '#20c997', back: '#0dcaf0' },
    ]

    setupCanvas()
    updateConfetti()

    confetti.addEventListener('click', addConfetti)
    window.addEventListener('resize', () => {
      setupCanvas()
    })

    // Confetti constructor
    function Conf() {
      this.randomModifier = rand(-1, 1)
      this.colorPair = colors[Math.floor(rand(0, colors.length))]
      this.dimensions = {
        x: rand(confettiParams.size.x[0], confettiParams.size.x[1]),
        y: rand(confettiParams.size.y[0], confettiParams.size.y[1]),
      }
      this.position = {
        x: clickPosition[0],
        y: clickPosition[1],
      }
      this.rotation = rand(0, 2 * Math.PI)
      this.scale = { x: 1, y: 1 }
      this.velocity = {
        x: rand(-confettiParams.initSpeed, confettiParams.initSpeed) * 0.4,
        y: rand(-confettiParams.initSpeed, confettiParams.initSpeed),
      }
      this.flipSpeed = rand(0.2, 1.5) * confettiParams.flipSpeed

      if (this.position.y <= container.h) {
        this.velocity.y = -Math.abs(this.velocity.y)
      }

      this.terminalVelocity = rand(1, 1.5) * confettiParams.terminalVelocity

      this.update = function () {
        this.velocity.x *= 0.98
        this.position.x += this.velocity.x

        this.velocity.y += this.randomModifier * confettiParams.drag
        this.velocity.y += confettiParams.gravity
        this.velocity.y = Math.min(this.velocity.y, this.terminalVelocity)
        this.position.y += this.velocity.y

        this.scale.y = Math.cos((this.position.y + this.randomModifier) * this.flipSpeed)
        this.color = this.scale.y > 0 ? this.colorPair.front : this.colorPair.back
      }
    }

    function updateConfetti() {
      confettiCtx.clearRect(0, 0, container.w, container.h)

      confettiElements.forEach((c) => {
        c.update()
        confettiCtx.translate(c.position.x, c.position.y)
        confettiCtx.rotate(c.rotation)
        const width = c.dimensions.x * c.scale.x
        const height = c.dimensions.y * c.scale.y
        confettiCtx.fillStyle = c.color
        confettiCtx.fillRect(-0.5 * width, -0.5 * height, width, height)
        confettiCtx.setTransform(1, 0, 0, 1, 0, 0)
      })

      confettiElements.forEach((c, idx) => {
        if (
          c.position.y > container.h ||
          c.position.x < -0.5 * container.x ||
          c.position.x > 1.5 * container.x
        ) {
          confettiElements.splice(idx, 1)
        }
      })
      window.requestAnimationFrame(updateConfetti)
    }

    function setupCanvas() {
      container = {
        w: confetti.clientWidth,
        h: confetti.clientHeight,
      }
      confetti.width = container.w
      confetti.height = container.h
    }

    function addConfetti(e) {
      const canvasBox = confetti.getBoundingClientRect()
      if (e) {
        clickPosition = [e.clientX - canvasBox.left, e.clientY - canvasBox.top]
      } else {
        clickPosition = [canvasBox.width * Math.random(), canvasBox.height * Math.random()]
      }
      for (let i = 0; i < confettiParams.number; i++) {
        confettiElements.push(new Conf())
      }
    }

    function confettiLoop() {
      addConfetti()
      const interval = setInterval(addConfetti, 700 + Math.random() * 700)
      window.setTimeout(() => {
        clearInterval(interval)
      }, 8000)
    }

    // eind confetti
  }
}
