import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import BacktestDashboard from './pages/BacktestDashboard';
import HistoricalWorldCup from './pages/HistoricalWorldCup';
import WorldCup2026 from './pages/WorldCup2026';
import MatchExplorer from './pages/MatchExplorer';
import TournamentSim from './pages/TournamentSim';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="sidebar">
          <div className="logo">⚽ WC 2026 Oracle</div>
          <NavLink to="/" end>Backtest</NavLink>
          <NavLink to="/history">Historical WC</NavLink>
          <NavLink to="/wc2026">WC 2026</NavLink>
          <NavLink to="/explorer">Match Explorer</NavLink>
          <NavLink to="/simulate">Tournament Sim</NavLink>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<BacktestDashboard />} />
            <Route path="/history" element={<HistoricalWorldCup />} />
            <Route path="/wc2026" element={<WorldCup2026 />} />
            <Route path="/explorer" element={<MatchExplorer />} />
            <Route path="/simulate" element={<TournamentSim />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
