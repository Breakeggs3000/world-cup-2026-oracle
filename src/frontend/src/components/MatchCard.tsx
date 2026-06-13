import { Wc2026Fixture } from '../api/client';
import { ProbabilityBar } from './ProbabilityBar';

export function MatchCard({ match }: { match: Wc2026Fixture }) {
  const played = match.status === 'played';
  const score = played ? `${match.home_score} – ${match.away_score}` : 'vs';

  return (
    <div className={`match-card ${played ? 'played' : 'upcoming'}`}>
      <div className="match-meta">
        <span className="match-date">{match.date}</span>
        <span className="match-group">Group {match.group}</span>
      </div>
      <div className="match-teams">
        <span className="team home">{match.home_team}</span>
        <span className="score">{score}</span>
        <span className="team away">{match.away_team}</span>
      </div>
      {match.probabilities && (
        <ProbabilityBar probs={match.probabilities} label="Prediction" />
      )}
      {match.likely_scoreline && (
        <div className="scoreline">Likely: {match.likely_scoreline}</div>
      )}
      {played && match.prediction_correct !== undefined && (
        <span className={`badge ${match.prediction_correct ? 'hit' : 'miss'}`}>
          {match.prediction_correct ? '✓ Hit' : '✗ Miss'} (pred: {match.predicted_outcome}, actual: {match.actual_outcome})
        </span>
      )}
    </div>
  );
}
