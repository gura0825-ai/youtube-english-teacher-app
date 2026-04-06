import { useState } from 'react'

interface Props {
  onSubmit: (url: string) => void;
  disabled: boolean;
}

export default function UrlInput({ onSubmit, disabled }: Props) {
  const [url, setUrl] = useState('')

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = url.trim()
    if (trimmed) onSubmit(trimmed)
  }

  return (
    <div className="url-input-card">
      <h2>YouTube English Teacher</h2>
      <p>Paste a YouTube URL to get a summary and 20-question quiz.</p>
      <form className="url-form" onSubmit={handleSubmit}>
        <input
          className="url-input"
          type="url"
          placeholder="https://www.youtube.com/watch?v=..."
          value={url}
          onChange={e => setUrl(e.target.value)}
          disabled={disabled}
          autoFocus
        />
        <button className="btn-primary" type="submit" disabled={disabled || !url.trim()}>
          Start
        </button>
      </form>
    </div>
  )
}
