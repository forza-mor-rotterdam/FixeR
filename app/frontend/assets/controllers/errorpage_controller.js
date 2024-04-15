import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['question', 'containerAnswers']
  connect() {
    const questions = [
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
      btn.textContent = questions[index].choices[i]
      btn.addEventListener('click', function () {
        window.alert(`${i}, ${i === questions[index].correct}`)
      })
      this.containerAnswersTarget.appendChild(btn)
    }
  }
}
