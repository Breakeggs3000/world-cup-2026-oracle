import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { api } from '../api/client';

export default function TournamentSim() {
  const [nSims, setNSims] = useState(10000);
  const [homeEloAdj, setHomeEloAdj] = useState(0);
  const [awayEloAdj, setAwayEloAdj] = useState(0);
  const [loading, setLoading] = useState(false);
  const [championData, setChampionData] = useState<Array<{ team: string; odds: number }>>([]);
  const [advanceData, setAdvanceData] = useState<Array<{ team: string; odds: number }>>([]);

  const runSim = async () => {
    setLoading(true);
    try {
      const result = await api.simulate({
        n_sims: nSims,
        home_elo_adj: homeEloAdj,
        away_elo_adj: awayEloAdj,
      });
      setChampionData(
        Object.entries(result.champion_odds)
          .map(([team, odds]) => ({ team, odds }))
          .sort((a, b) => b.odds - a.odds)
          .slice(0, 12)
      );
      setAdvanceData(
        Object.entries(result.group_advance_odds)
          .map(([team, odds]) => ({ team, odds }))
          .sort((a, b) => b.odds - a.odds)
          .slice(0, 16)
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h1>Tournament Simulation</h1>
      <p className="subtitle">Monte Carlo simulation of WC 2026 group stage + knockout</p>

      <div className="controls sim-controls">
        <label>
          Simulations: {nSims.toLocaleString()}
          <input type="range" min={1000} max={20000} step={1000} value={nSims} onChange={(e) => setNSims(Number(e.target.value))} />
        </label>
        <label>
          Home Elo adj: {homeEloAdj}
          <input type="range" min={-100} max={100} value={homeEloAdj} onChange={(e) => setHomeEloAdj(Number(e.target.value))} />
        </label>
        <label>
          Away Elo adj: {awayEloAdj}
          <input type="range" min={-100} max={100} value={awayEloAdj} onChange={(e) => setAwayEloAdj(Number(e.target.value))} />
        </label>
        <button className="primary-btn" onClick={runSim} disabled={loading}>
          {loading ? 'Running…' : `Run ${nSims.toLocaleString()} simulations`}
        </button>
      </div>

      {championData.length > 0 && (
        <div className="chart-container">
          <h2>Champion Odds (top 12)</h2>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={championData} layout="vertical" margin={{ left: 80 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis type="number" domain={[0, 'auto']} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
              <YAxis type="category" dataKey="team" width={75} />
              <Tooltip formatter={(v: number) => `${(v * 100).toFixed(1)}%`} />
              <Bar dataKey="odds" fill="#f59e0b" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {advanceData.length > 0 && (
        <div className="chart-container">
          <h2>Group Advance Odds (top 16)</h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={advanceData} layout="vertical" margin={{ left: 80 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis type="number" domain={[0, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
              <YAxis type="category" dataKey="team" width={75} />
              <Tooltip formatter={(v: number) => `${(v * 100).toFixed(1)}%`} />
              <Bar dataKey="odds" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
