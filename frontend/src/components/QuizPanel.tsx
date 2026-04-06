import { useState } from 'react'
import { QuizItem } from '../types'

interface Props {
  quiz: QuizItem[];
}

type Answers  = Record<number, string>   // { questionId: chosenKey }
type Revealed = Record<number, boolean>  // { questionId: feedbackShown }

const OPTION_KEYS = ['A', 'B', 'C', 'D'] as const

export default function QuizPanel({ quiz }: Props) {
  const [answers, setAnswers]   = useState<Answers>({})
  const [revealed, setRevealed] = useState<Revealed>({})

  function handleSelect(questionId: number, key: string, correctAnswer: string) {
    if (revealed[questionId]) return  // already answered

    setAnswers(prev => ({ ...prev, [questionId]: key }))
    setRevealed(prev => ({ ...prev, [questionId]: true }))

    // If correct, no extra action needed
    // If wrong, the reveal shows the correct answer highlighted
    void correctAnswer  // suppress unused warning
  }

  const answeredCount = Object.keys(revealed).length
  const correctCount  = Object.entries(revealed)
    .filter(([id, isRevealed]) => isRevealed && answers[Number(id)] === quiz.find(q => q.id === Number(id))?.answer)
    .length

  return (
    <div className="tab-panel">
      <div className="quiz-score-bar">
        <span className="score-label">Progress</span>
        <span className="score-value">
          {answeredCount === 0
            ? 'Not started'
            : `Score: ${correctCount} / ${answeredCount} answered`}
        </span>
      </div>

      <ol className="quiz-list">
        {quiz.map(item => {
          const isRevealed = !!revealed[item.id]
          const chosen     = answers[item.id]

          return (
            <li key={item.id} className={`quiz-item ${isRevealed ? 'answered' : ''}`}>
              <p className="question-text">
                <span className="question-num">Q{item.id}.&nbsp;</span>
                {item.question}
              </p>

              <div className="options-list">
                {OPTION_KEYS.map(key => {
                  const isChosen  = chosen === key
                  const isCorrect = key === item.answer

                  let btnClass = 'option-btn'
                  if (isRevealed) {
                    if (isChosen && isCorrect)  btnClass += ' correct'
                    else if (isChosen && !isCorrect) btnClass += ' wrong'
                    else if (!isChosen && isCorrect) btnClass += ' reveal-correct'
                  }

                  return (
                    <button
                      key={key}
                      className={btnClass}
                      disabled={isRevealed}
                      onClick={() => handleSelect(item.id, key, item.answer)}
                    >
                      <span className="option-key">{key}</span>
                      {item.options[key]}
                    </button>
                  )
                })}
              </div>

              {isRevealed && (
                <p className={`feedback ${chosen === item.answer ? 'correct' : 'wrong'}`}>
                  {chosen === item.answer
                    ? '✓ Correct!'
                    : `✗ Wrong — correct answer: ${item.answer}`}
                </p>
              )}
            </li>
          )
        })}
      </ol>
    </div>
  )
}
