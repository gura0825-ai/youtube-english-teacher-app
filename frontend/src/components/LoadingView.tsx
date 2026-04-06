import { useEffect, useState } from 'react'

const STEPS = [
  'Fetching transcript...',
  'Analyzing content...',
  'Generating quiz...',
]

const STEP_DELAYS = [0, 6000, 16000]   // ms after start to show each step as active
const STILL_WORKING_DELAY = 30_000     // ms before showing "Still working..." message

export default function LoadingView() {
  const [activeStep, setActiveStep] = useState(0)
  const [showStillWorking, setShowStillWorking] = useState(false)

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = []

    STEP_DELAYS.forEach((delay, i) => {
      if (delay > 0) {
        timers.push(setTimeout(() => setActiveStep(i), delay))
      }
    })

    timers.push(setTimeout(() => setShowStillWorking(true), STILL_WORKING_DELAY))

    return () => timers.forEach(clearTimeout)
  }, [])

  return (
    <div className="loading-card">
      <div className="spinner" />
      <ul className="loading-steps">
        {STEPS.map((label, i) => {
          const isDone = i < activeStep
          const isActive = i === activeStep
          return (
            <li key={i} className={`loading-step ${isDone ? 'done' : ''} ${isActive ? 'active' : ''}`}>
              <span className="step-icon">
                {isDone ? '✓' : i + 1}
              </span>
              {label}
            </li>
          )
        })}
      </ul>
      {showStillWorking && (
        <p className="still-working">Still working, this may take a moment&hellip;</p>
      )}
    </div>
  )
}
