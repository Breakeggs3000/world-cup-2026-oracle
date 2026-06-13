import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import BacktestDashboard from './pages/BacktestDashboard';
import HistoricalWorldCup from './pages/HistoricalWorldCup';
import WorldCup2026 from './pages/WorldCup2026';
import MatchExplorer from './pages/MatchExplorer';
import TournamentSim from './pages/TournamentSim';
import { DisclaimerBanner } from './components/DisclaimerBanner';
import { LanguageSelector } from './components/LanguageSelector';
import './App.css';

function App() {
  const { t } = useTranslation();
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="sidebar">
          <div className="logo">⚽ {t('app.title')}</div>
          <NavLink to="/" end>{t('nav.backtest')}</NavLink>
          <NavLink to="/history">{t('nav.history')}</NavLink>
          <NavLink to="/wc2026">{t('nav.wc2026')}</NavLink>
          <NavLink to="/explorer">{t('nav.explorer')}</NavLink>
          <NavLink to="/simulate">{t('nav.simulate')}</NavLink>
          <div className="sidebar-footer">
            <LanguageSelector />
          </div>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<BacktestDashboard />} />
            <Route path="/history" element={<HistoricalWorldCup />} />
            <Route path="/wc2026" element={<WorldCup2026 />} />
            <Route path="/explorer" element={<MatchExplorer />} />
            <Route path="/simulate" element={<TournamentSim />} />
          </Routes>
          <DisclaimerBanner />
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
