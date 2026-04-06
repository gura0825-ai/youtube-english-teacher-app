import { useState } from 'react'
import { processVideo } from './api/client'
import { AppPhase, ProcessResponse } from './types'
import UrlInput from './components/UrlInput'
import LoadingView from './components/LoadingView'
import TabView from './components/TabView'

export default function App() {
  const [phase, setPhase]               = useState<AppPhase>('idle')
  const [result, setResult]             = useState<ProcessResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  async function handleSubmit(url: string) {
    setPhase('loading')
    setResult(null)
    setErrorMessage(null)

    try {
      const data = await processVideo(url)
      setResult(data)
      setPhase('done')
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : 'Unexpected error. Please try again.')
      setPhase('error')
    }
  }

  function handleReset() {
    setPhase('idle')
    setResult(null)
    setErrorMessage(null)
  }

  return (
    <>
      <header className="app-header">
        <div className="logo-icon">YT</div>
        <h1>YouTube English Teacher</h1>
      </header>

      <main className="app-main">
        {(phase === 'idle' || phase === 'error') && (
          <>
            <UrlInput onSubmit={handleSubmit} disabled={false} />
            {errorMessage && (
              <div className="error-banner">
                <span>⚠</span>
                <span>{errorMessage}</span>
              </div>
            )}
          </>
        )}

        {phase === 'loading' && <LoadingView />}

        {phase === 'done' && result && (
          <TabView result={result} onReset={handleReset} />
        )}
      </main>
    </>
  )
}
