import { useEffect, useState } from 'react';
import { api, BacktestSummary } from '../api/client';
import { MetricsCards } from '../components/MetricsCards';
import { CalibrationChart } from '../components/CalibrationChart';

export default function BacktestDashboard() {
  const [data, setData] = useState<BacktestSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getBacktestSummary()
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error">Failed to load backtest: {error}</div>;
  if (!data) return <div className="loading">Loading backtest metrics…</div>;

  const metrics = [
    { label: 'Test Accuracy', value: `${(data.test.accuracy * 100).toFixed(1)}%`, highlight: true },
    { label: 'Naive Baseline', value: `${(data.naive_baseline_test_accuracy * 100).toFixed(1)}%` },
    { label: 'Beats Naive By', value: `${(data.beats_naive_by * 100).toFixed(1)}%`, highlight: data.beats_naive_by > 0 },
    { label: 'RPS (test)', value: data.test.rps.toFixed(3) },
    { label: 'Log-loss (test)', value: data.test.log_loss.toFixed(3) },
    { label: 'Brier (test)', value: data.test.brier.toFixed(3) },
    { label: 'Val Accuracy', value: `${(data.validation.accuracy * 100).toFixed(1)}%`, sub: `${data.validation.count} matches` },
    { label: 'Test Matches', value: String(data.test.count) },
  ];

  const wcRows = Object.entries(data.world_cups)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([year, m]) => ({ year, accuracy: m.accuracy, rps: m.rps, count: m.count }));

  return (
    <div className="page">
      <h1>Backtest Dashboard</h1>
      <p className="subtitle">
        Walk-forward evaluation — train ≤2017, validate 2018–2022, test 2023+
      </p>
      <MetricsCards items={metrics} />
      <CalibrationChart data={data.calibration} />

      <section className="section">
        <h2>Per-World Cup Accuracy</h2>
        <table className="data-table">
          <thead>
            <tr><th>Year</th><th>Accuracy</th><th>RPS</th><th>Matches</th></tr>
          </thead>
          <tbody>
            {wcRows.map((r) => (
              <tr key={r.year}>
                <td>{r.year}</td>
                <td>{(r.accuracy * 100).toFixed(1)}%</td>
                <td>{r.rps.toFixed(3)}</td>
                <td>{r.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="section">
        <h2>Confusion Matrix (test)</h2>
        <table className="data-table confusion">
          <thead>
            <tr><th>Actual ↓ / Pred →</th><th>W</th><th>D</th><th>L</th></tr>
          </thead>
          <tbody>
            {['W', 'D', 'L'].map((actual) => (
              <tr key={actual}>
                <td>{actual}</td>
                <td>{data.confusion_matrix[actual]?.W ?? 0}</td>
                <td>{data.confusion_matrix[actual]?.D ?? 0}</td>
                <td>{data.confusion_matrix[actual]?.L ?? 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
