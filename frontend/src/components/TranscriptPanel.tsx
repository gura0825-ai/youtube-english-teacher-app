interface Props {
  transcript: string;
}

export default function TranscriptPanel({ transcript }: Props) {
  return (
    <div className="tab-panel">
      <pre className="transcript-text">{transcript}</pre>
    </div>
  )
}
