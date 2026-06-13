import { ScoreOutcome } from '../api/client';

export function TopOutcomes({ outcomes, label = 'Top scorelines' }: { outcomes: ScoreOutcome[]; label?: string }) {
  if (!outcomes.length) return null;

  return (
    <div className="top-outcomes">
      <div className="top-outcomes-label">{label}</div>
      <ol className="top-outcomes-list">
        {outcomes.map((o) => (
          <li key={o.score}>
            <span className="outcome-score">{o.score}</span>
            <span className="outcome-pct">{(o.probability * 100).toFixed(1)}%</span>
          </li>
        ))}
      </ol>
    </div>
  );
}
