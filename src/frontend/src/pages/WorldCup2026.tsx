import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { TFunction } from 'i18next';
import { api, Wc2026Fixture } from '../api/client';
import { MatchCard } from '../components/MatchCard';

type Tab = 'all' | 'upcoming' | 'played';

function formatAgo(iso: string | undefined, t: TFunction): string {
  if (!iso) return '';
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.max(0, Math.round(diff / 60000));
  if (mins < 1) return t('common.updatedAgo', { time: 'just now' });
  return t('common.updatedAgo', { time: `${mins}m ago` });
}

export default function WorldCup2026() {
  const { t } = useTranslation();
  const [tab, setTab] = useState<Tab>('all');
  const [group, setGroup] = useState('');
  const [sort, setSort] = useState<'datetime' | 'date'>('datetime');
  const [order, setOrder] = useState<'asc' | 'desc'>('asc');
  const [fixtures, setFixtures] = useState<Wc2026Fixture[]>([]);
  const [lastSynced, setLastSynced] = useState<string | undefined>();
  const [dataSource, setDataSource] = useState('seed');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    api.getWc2026Fixtures(tab, { sort, order, group: group || undefined })
      .then((r) => {
        setFixtures(r.fixtures);
        setLastSynced(r.last_synced_at);
        setDataSource(r.data_source || 'seed');
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [tab, sort, order, group]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    const id = window.setInterval(() => {
      if (document.visibilityState === 'visible') load();
    }, 60000);
    return () => window.clearInterval(id);
  }, [load]);

  const played = fixtures.filter((f) => f.status === 'played');
  const hits = played.filter((f) => f.prediction_correct).length;

  return (
    <div className="page">
      <h1>{t('wc2026.title')}</h1>
      <p className="subtitle">{t('wc2026.subtitle')}</p>

      <div className="controls-row">
        <div className="tabs">
          {(['all', 'upcoming', 'played'] as Tab[]).map((tname) => (
            <button key={tname} className={tab === tname ? 'active' : ''} onClick={() => setTab(tname)}>
              {t(`common.${tname}`)}
            </button>
          ))}
        </div>
        <button type="button" className="refresh-btn" onClick={load}>{t('common.refresh')}</button>
      </div>

      <div className="controls filters-row">
        <label>
          {t('common.group')}
          <select value={group} onChange={(e) => setGroup(e.target.value)}>
            <option value="">{t('common.all')}</option>
            {'ABCDEFGHIJKL'.split('').map((g) => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>
        </label>
        <label>
          {t('common.sortKickoff')}
          <select value={sort} onChange={(e) => setSort(e.target.value as 'datetime' | 'date')}>
            <option value="datetime">{t('common.sortKickoff')}</option>
            <option value="date">{t('common.sortDate')}</option>
          </select>
        </label>
        <label>
          <select value={order} onChange={(e) => setOrder(e.target.value as 'asc' | 'desc')}>
            <option value="asc">{t('common.orderEarliest')}</option>
            <option value="desc">{t('common.orderLatest')}</option>
          </select>
        </label>
      </div>

      <p className="meta-line">
        {formatAgo(lastSynced, t)}
        {dataSource && ` · ${t('wc2026.syncSource', { source: dataSource })}`}
      </p>

      {error && <div className="error">{t('common.errorLoad')}: {error}</div>}
      {loading && !error && <div className="loading">{t('common.loading')}</div>}

      {!loading && !error && tab === 'played' && played.length > 0 && (
        <p className="summary-line">
          {t('wc2026.predictionsSummary', { hits, total: played.length })}
        </p>
      )}

      <div className="match-list">
        {fixtures.map((f) => <MatchCard key={f.id} match={f} />)}
      </div>
    </div>
  );
}
