import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

interface CalibrationBin {
  bin: number;
  count: number;
  avg_confidence: number;
  accuracy: number;
}

export function CalibrationChart({ data }: { data: CalibrationBin[] }) {
  if (!data.length) return <p className="empty">No calibration data</p>;

  return (
    <div className="chart-container">
      <h3>Calibration (test set)</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="bin" label={{ value: 'Confidence bin', position: 'insideBottom', offset: -5 }} />
          <YAxis domain={[0, 1]} />
          <Tooltip />
          <Bar dataKey="avg_confidence" name="Predicted" fill="#3b82f6" />
          <Bar dataKey="accuracy" name="Actual" fill="#22c55e" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
