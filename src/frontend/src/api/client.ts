const API_ORIGIN = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '');
const BASE = API_ORIGIN ? `${API_ORIGIN}/api` : '/api';
const REQUEST_TIMEOUT_MS = 120_000;

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  if (import.meta.env.PROD && !API_ORIGIN) {
    throw new Error(
      'VITE_API_URL is not set. In Vercel → Settings → Environment Variables, set it to your Railway backend URL ' +
        '(e.g. https://your-app.up.railway.app — no trailing slash, no /api), then redeploy.'
    );
  }

  const url = `${BASE}${path}`;
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    const contentType = res.headers.get('content-type') ?? '';

    if (!res.ok) {
      throw new Error(`API error ${res.status} from ${url}`);
    }

    if (!contentType.includes('application/json')) {
      throw new Error(
        `Expected JSON from ${url} but got ${contentType || 'unknown content-type'}. ` +
          'Usually VITE_API_URL is missing/wrong or Vercel was not redeployed after setting it. ' +
          `Current VITE_API_URL: ${API_ORIGIN || '(empty — using /api on Vercel, which returns HTML)'}.`
      );
    }

    return res.json();
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new Error(
        `API timed out after ${REQUEST_TIMEOUT_MS / 1000}s (${url}). ` +
          'Backend may be waking up — wait 60s and refresh.'
      );
    }
    if (err instanceof SyntaxError) {
      throw new Error(
        `Invalid JSON from ${url}. The server returned HTML instead of JSON — ` +
          'check VITE_API_URL points to your Railway backend and redeploy Vercel.'
      );
    }
    throw err;
  } finally {
    window.clearTimeout(timeout);
  }
}

export interface Probabilities {
  W: number;
  D: number;
  L: number;
}

export interface BacktestSummary {
  validation: { accuracy: number; log_loss: number; brier: number; rps: number; count: number };
  test: { accuracy: number; log_loss: number; brier: number; rps: number; count: number };
  naive_baseline_test_accuracy: number;
  beats_naive_by: number;
  calibration: Array<{ bin: number; count: number; avg_confidence: number; accuracy: number }>;
  world_cups: Record<string, { accuracy: number; rps: number; count: number }>;
  confusion_matrix: Record<string, Record<string, number>>;
  splits: Record<string, string>;
}

export interface MatchPrediction {
  date: string;
  home_team: string;
  away_team: string;
  home_score?: number;
  away_score?: number;
  tournament?: string;
  city?: string;
  predicted?: Probabilities;
  predicted_outcome?: string;
  actual?: string;
  correct?: boolean;
}

export interface ScoreOutcome {
  score: string;
  probability: number;
}

export interface Wc2026Fixture {
  id: string;
  date: string;
  home_team: string;
  away_team: string;
  stage: string;
  group: string;
  venue: string;
  neutral: boolean;
  status: string;
  home_score?: number;
  away_score?: number;
  probabilities?: Probabilities;
  predicted_outcome?: string;
  likely_scoreline?: string;
  top_outcomes?: ScoreOutcome[];
  actual_outcome?: string;
  prediction_correct?: boolean;
}

export const api = {
  getBacktestSummary: () => request<BacktestSummary>('/backtest/summary'),
  getTournamentYears: () => request<{ years: number[] }>('/tournaments'),
  getTournamentMatches: (year: number) =>
    request<{ year: number; matches: MatchPrediction[]; summary: { total: number; correct: number; accuracy: number } }>(
      `/tournaments/${year}/matches`
    ),
  getWc2026Fixtures: (status: string = 'all') =>
    request<{ fixtures: Wc2026Fixture[]; count: number }>(`/wc2026/fixtures?status=${status}`),
  getWc2026Standings: () => request<{ standings: Record<string, Array<Record<string, number | string>>> }>('/wc2026/standings'),
  predict: (home: string, away: string, neutral = true) =>
    request<Record<string, unknown>>(`/predict?home=${encodeURIComponent(home)}&away=${encodeURIComponent(away)}&neutral=${neutral}`),
  predictScenario: (body: Record<string, unknown>) =>
    request<Record<string, unknown>>('/predict/scenario', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  simulate: (body: { n_sims: number; home_elo_adj?: number; away_elo_adj?: number; form_boost_home?: number; form_boost_away?: number }) =>
    request<{ n_sims: number; champion_odds: Record<string, number>; group_advance_odds: Record<string, number> }>(
      '/simulate/wc2026',
      { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }
    ),
};
