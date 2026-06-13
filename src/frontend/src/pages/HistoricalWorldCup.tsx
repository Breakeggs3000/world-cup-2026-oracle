import { useEffect, useState } from 'react';
import { api, MatchPrediction } from '../api/client';
import { ProbabilityBar } from '../components/ProbabilityBar';

export default function HistoricalWorldCup() {
  const [years, setYears] = useState<number[]>([]);
  const [year, setYear] = useState(2022);
  const [matches, setMatches] = useState<MatchPrediction[]>([]);
  const [summary, setSummary] = useState({ total: 0, correct: 0, accuracy: 0 });
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getTournamentYears().then((r) => {
      setYears(r.years);
      if (r.years.length) setYear(r.years[r.years.length - 1]);
    }).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api.getTournamentMatches(year)
      .then((r) => {
        setMatches(r.matches);
        setSummary(r.summary);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [year]);

  const filtered = matches.filter((m) => {
    if (filter === 'correct') return m.correct;
    if (filter === 'wrong') return m.correct === false;
    return true;
  });

  return (
    <div className="page">
      <h1>Historical World Cups</h1>
      <div className="controls">
        <label>
          Tournament
          <select value={year} onChange={(e) => setYear(Number(e.target.value))}>
            {years.map((y) => <option key={y} value={y}>{y}</option>)}
          </select>
        </label>
        <label>
          Filter
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">All matches</option>
            <option value="correct">Correct only</option>
            <option value="wrong">Wrong only</option>
          </select>
        </label>
      </div>
      {error && <div className="error">Failed to load matches: {error}. Is the backend running on port 8000?</div>}
      {loading && !error && (
        <div className="loading">Loading matches and predictions… (first load may take a few minutes while the model warms up)</div>
      )}
      {!loading && !error && (
        <p className="summary-line">
          Model got <strong>{summary.correct}</strong> / <strong>{summary.total}</strong> matches correct
          ({(summary.accuracy * 100).toFixed(1)}%)
        </p>
      )}
      <div className="match-list">
        {filtered.map((m, i) => (
          <div key={i} className={`match-card ${m.correct ? 'hit' : 'miss'}`}>
            <div className="match-meta">
              <span>{m.date}</span>
              <span>{m.city || m.tournament}</span>
            </div>
            <div className="match-teams">
              <span>{m.home_team}</span>
              <span className="score">{m.home_score} – {m.away_score}</span>
              <span>{m.away_team}</span>
            </div>
            {m.predicted && <ProbabilityBar probs={m.predicted} />}
            <div className="match-result">
              Pred: <strong>{m.predicted_outcome}</strong> · Actual: <strong>{m.actual}</strong>
              <span className={`badge ${m.correct ? 'hit' : 'miss'}`}>{m.correct ? '✓' : '✗'}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
