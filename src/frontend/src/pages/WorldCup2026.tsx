import { useEffect, useState } from 'react';
import { api, Wc2026Fixture } from '../api/client';
import { MatchCard } from '../components/MatchCard';

type Tab = 'all' | 'upcoming' | 'played';

export default function WorldCup2026() {
  const [tab, setTab] = useState<Tab>('all');
  const [fixtures, setFixtures] = useState<Wc2026Fixture[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api.getWc2026Fixtures(tab)
      .then((r) => setFixtures(r.fixtures))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [tab]);

  const played = fixtures.filter((f) => f.status === 'played');
  const hits = played.filter((f) => f.prediction_correct).length;

  return (
    <div className="page">
      <h1>World Cup 2026</h1>
      <p className="subtitle">Group stage underway — June 11–July 19, 2026</p>

      <div className="tabs">
        {(['all', 'upcoming', 'played'] as Tab[]).map((t) => (
          <button key={t} className={tab === t ? 'active' : ''} onClick={() => setTab(t)}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {error && <div className="error">Failed to load fixtures: {error}. Is the backend running on port 8000?</div>}
      {loading && !error && (
        <div className="loading">Loading fixtures and predictions… (first load may take a few minutes while the model warms up)</div>
      )}

      {!loading && !error && tab === 'played' && played.length > 0 && (
        <p className="summary-line">
          Predictions: <strong>{hits}</strong> / <strong>{played.length}</strong> correct
        </p>
      )}

      <div className="match-list">
        {fixtures.map((f) => <MatchCard key={f.id} match={f} />)}
      </div>
    </div>
  );
}
