interface Props {
  homeEloAdj: number;
  awayEloAdj: number;
  formBoostHome: number;
  formBoostAway: number;
  isKnockout: boolean;
  onChange: (field: string, value: number | boolean) => void;
}

export default function ScenarioSliders({
  homeEloAdj,
  awayEloAdj,
  formBoostHome,
  formBoostAway,
  isKnockout,
  onChange,
}: Props) {
  return (
    <div className="sliders">
      <label>
        Home Elo adj ({homeEloAdj})
        <input type="range" min={-100} max={100} value={homeEloAdj} onChange={(e) => onChange("homeEloAdj", +e.target.value)} />
      </label>
      <label>
        Away Elo adj ({awayEloAdj})
        <input type="range" min={-100} max={100} value={awayEloAdj} onChange={(e) => onChange("awayEloAdj", +e.target.value)} />
      </label>
      <label>
        Home form boost ({formBoostHome.toFixed(2)})
        <input type="range" min={-0.3} max={0.3} step={0.05} value={formBoostHome} onChange={(e) => onChange("formBoostHome", +e.target.value)} />
      </label>
      <label>
        Away form boost ({formBoostAway.toFixed(2)})
        <input type="range" min={-0.3} max={0.3} step={0.05} value={formBoostAway} onChange={(e) => onChange("formBoostAway", +e.target.value)} />
      </label>
      <label className="checkbox">
        <input type="checkbox" checked={isKnockout} onChange={(e) => onChange("isKnockout", e.target.checked)} />
        Knockout stage
      </label>
    </div>
  );
}
