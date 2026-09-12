import { TranscriptSegment } from '../types'

interface Props {
  transcript: TranscriptSegment[];
}

export default function TranscriptPanel({ transcript }: Props) {
  return (
    <div className="tab-panel">
      <div className="transcript-list">
        {transcript.map((segment, i) => (
          <div className="transcript-line" key={i}>
            <span className="transcript-time">{segment.time}</span>
            <span className="transcript-line-text">{segment.text}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

