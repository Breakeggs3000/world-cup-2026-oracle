interface Props {
  value: string;
  onChange: (team: string) => void;
  teams: string[];
  label: string;
}

export default function TeamSelect({ value, onChange, teams, label }: Props) {
  return (
    <label>
      {label}
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {teams.map((t) => (
          <option key={t} value={t}>
            {t}
          </option>
        ))}
      </select>
    </label>
  );
}
