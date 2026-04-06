interface Props {
  summary: string;
  insights: string[];
}

export default function SummaryPanel({ summary, insights }: Props) {
  return (
    <div className="tab-panel">
      <div className="summary-section">
        <h3>Summary</h3>
        <p className="summary-text">{summary}</p>
        <h3>Key Insights</h3>
        <ul className="insights-list">
          {insights.map((insight, i) => (
            <li key={i} className="insight-card">
              <span className="insight-num">{i + 1}</span>
              <span className="insight-text">{insight}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
