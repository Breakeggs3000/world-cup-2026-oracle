import { Probabilities } from '../api/client';

export function ProbabilityBar({ probs, label }: { probs: Probabilities; label?: string }) {
  const w = (probs.W ?? 0) * 100;
  const d = (probs.D ?? 0) * 100;
  const l = (probs.L ?? 0) * 100;

  return (
    <div className="prob-bar">
      {label && <div className="prob-label">{label}</div>}
      <div className="prob-track">
        <div className="prob-seg win" style={{ width: `${w}%` }} title={`Home win ${w.toFixed(0)}%`} />
        <div className="prob-seg draw" style={{ width: `${d}%` }} title={`Draw ${d.toFixed(0)}%`} />
        <div className="prob-seg loss" style={{ width: `${l}%` }} title={`Away win ${l.toFixed(0)}%`} />
      </div>
      <div className="prob-legend">
        <span>W {(probs.W ?? 0).toFixed(0)}%</span>
        <span>D {(probs.D ?? 0).toFixed(0)}%</span>
        <span>L {(probs.L ?? 0).toFixed(0)}%</span>
      </div>
    </div>
  );
}
