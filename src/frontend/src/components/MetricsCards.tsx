interface MetricCardProps {
  label: string;
  value: string;
  sub?: string;
  highlight?: boolean;
}

export function MetricsCards({ items }: { items: MetricCardProps[] }) {
  return (
    <div className="metrics-grid">
      {items.map((item) => (
        <div key={item.label} className={`metric-card ${item.highlight ? 'highlight' : ''}`}>
          <div className="metric-label">{item.label}</div>
          <div className="metric-value">{item.value}</div>
          {item.sub && <div className="metric-sub">{item.sub}</div>}
        </div>
      ))}
    </div>
  );
}
