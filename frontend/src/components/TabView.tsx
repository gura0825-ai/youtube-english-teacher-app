import { useState } from 'react'
import { ProcessResponse } from '../types'
import TranscriptPanel from './TranscriptPanel'
import SummaryPanel from './SummaryPanel'
import QuizPanel from './QuizPanel'

interface Props {
  result: ProcessResponse;
  onReset: () => void;
}

type Tab = 'transcript' | 'summary' | 'quiz'

const TABS: { id: Tab; label: string }[] = [
  { id: 'transcript', label: 'Transcript' },
  { id: 'summary',    label: 'Summary' },
  { id: 'quiz',       label: 'Quiz' },
]

export default function TabView({ result, onReset }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>('summary')

  return (
    <div className="result-container">
      <div className="result-header">
        <p className="result-title" title={result.title}>{result.title}</p>
        <p className="result-vid">video id: {result.video_id}</p>
      </div>

      <div className="tab-bar">
        {TABS.map(tab => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'transcript' && <TranscriptPanel transcript={result.transcript} />}
      {activeTab === 'summary'    && <SummaryPanel summary={result.summary} insights={result.insights} />}
      {activeTab === 'quiz'       && <QuizPanel quiz={result.quiz} />}

      <button className="btn-primary btn-new-url" onClick={onReset}>
        Try another video
      </button>
    </div>
  )
}
