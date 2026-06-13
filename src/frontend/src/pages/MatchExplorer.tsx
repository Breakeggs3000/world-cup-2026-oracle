import { useEffect, useState, useCallback } from 'react';
import { api, Probabilities, ScoreOutcome } from '../api/client';
import { ProbabilityBar } from '../components/ProbabilityBar';
import { TopOutcomes } from '../components/TopOutcomes';

const TEAMS = [
  'Brazil', 'Argentina', 'France', 'Germany', 'England', 'Spain', 'Portugal',
  'Netherlands', 'Belgium', 'Italy', 'USA', 'Mexico', 'Japan', 'Morocco',
  'Croatia', 'Uruguay', 'Colombia', 'Switzerland', 'Senegal', 'South Korea',
  'Australia', 'Canada', 'Denmark', 'Poland', 'Iran', 'Ghana', 'Ecuador',
];

export default function MatchExplorer() {
  const [home, setHome] = useState('Brazil');
  const [away, setAway] = useState('Morocco');
  const [homeEloAdj, setHomeEloAdj] = useState(0);
  const [awayEloAdj, setAwayEloAdj] = useState(0);
  const [formHome, setFormHome] = useState(0);
  const [formAway, setFormAway] = useState(0);
  const [knockout, setKnockout] = useState(false);
  const [probs, setProbs] = useState<Probabilities | null>(null);
  const [scoreline, setScoreline] = useState('');
  const [topOutcomes, setTopOutcomes] = useState<ScoreOutcome[]>([]);
  const [predicted, setPredicted] = useState('');

  const fetchPrediction = useCallback(() => {
    api.predictScenario({
      home, away, neutral: true, is_knockout: knockout,
      home_elo_adj: homeEloAdj, away_elo_adj: awayEloAdj,
      form_boost_home: formHome, form_boost_away: formAway,
    }).then((r) => {
      setProbs(r.probabilities as Probabilities);
      setScoreline(String(r.likely_scoreline || ''));
      setTopOutcomes((r.top_outcomes as ScoreOutcome[]) || []);
      setPredicted(String(r.predicted_outcome || ''));
    });
  }, [home, away, homeEloAdj, awayEloAdj, formHome, formAway, knockout]);

  useEffect(() => { fetchPrediction(); }, [fetchPrediction]);

  return (
    <div className="page">
      <h1>Match Explorer</h1>
      <p className="subtitle">Tweak scenario sliders and see live probability updates</p>

      <div className="explorer-grid">
        <div className="controls-panel">
          <label>
            Home team
            <select value={home} onChange={(e) => setHome(e.target.value)}>
              {TEAMS.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </label>
          <label>
            Away team
            <select value={away} onChange={(e) => setAway(e.target.value)}>
              {TEAMS.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </label>
          <label>
            Home Elo adj ({homeEloAdj})
            <input type="range" min={-100} max={100} value={homeEloAdj} onChange={(e) => setHomeEloAdj(Number(e.target.value))} />
          </label>
          <label>
            Away Elo adj ({awayEloAdj})
            <input type="range" min={-100} max={100} value={awayEloAdj} onChange={(e) => setAwayEloAdj(Number(e.target.value))} />
          </label>
          <label>
            Home form boost ({formHome.toFixed(2)})
            <input type="range" min={-0.3} max={0.3} step={0.05} value={formHome} onChange={(e) => setFormHome(Number(e.target.value))} />
          </label>
          <label>
            Away form boost ({formAway.toFixed(2)})
            <input type="range" min={-0.3} max={0.3} step={0.05} value={formAway} onChange={(e) => setFormAway(Number(e.target.value))} />
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={knockout} onChange={(e) => setKnockout(e.target.checked)} />
            Knockout stage
          </label>
        </div>

        <div className="result-panel">
          <div className="match-teams large">
            <span>{home}</span>
            <span className="vs">vs</span>
            <span>{away}</span>
          </div>
          {probs && <ProbabilityBar probs={probs} label="W / D / L probabilities" />}
          <div className="prediction-summary">
            <p>Predicted outcome: <strong>{predicted}</strong></p>
            <p>Most likely scoreline: <strong>{scoreline}</strong></p>
            {topOutcomes.length > 0 && <TopOutcomes outcomes={topOutcomes} />}
          </div>
        </div>
      </div>
    </div>
  );
}
