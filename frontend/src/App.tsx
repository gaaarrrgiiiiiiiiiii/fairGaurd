import { Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import Dashboard from './pages/Dashboard';
import Auth from './pages/Auth';
import Reports from './pages/Reports';
import Models from './pages/Models';
import Settings from './pages/Settings';

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/auth" element={<Auth />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/dashboard/reports" element={<Reports />} />
      <Route path="/dashboard/models" element={<Models />} />
      <Route path="/dashboard/settings" element={<Settings />} />
    </Routes>
  );
}

export default App;
