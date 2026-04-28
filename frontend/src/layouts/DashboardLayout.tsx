import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../components/LandingPage.css';
import './DashboardLayout.css';

interface DashboardLayoutProps {
  children: React.ReactNode;
  headerContent?: React.ReactNode;
}

export default function DashboardLayout({ children, headerContent }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  // Derive display name — fall back gracefully
  const displayName = user?.name || 'Admin User';
  const displayRole = user?.organization || 'Enterprise';
  const avatarLetter = displayName.charAt(0).toUpperCase();

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  return (
    <div className={`dashboard-layout lp-root ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
      {/* ── Sidebar ──────────────────────────────────────────────── */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <Link to="/" className="sidebar-logo">
            <div className="sidebar-logo-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="#CCFF00" strokeWidth="2" strokeLinecap="round" width="16" height="16">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            <span className="sidebar-logo-text">
              FAIR<span className="logo-accent">GUARD</span>
            </span>
          </Link>
          <button className="sidebar-toggle" onClick={toggleSidebar} aria-label="Toggle sidebar">
            {sidebarOpen ? (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 18 9 12 15 6"/></svg>
            ) : (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6"/></svg>
            )}
          </button>
        </div>

        <nav className="sidebar-nav">
          <span className="sidebar-nav-label">Core</span>

          <Link
            to="/dashboard"
            className={`sidebar-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
            title="Real-time Engine"
          >
            <span className="sidebar-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            </span>
            <span className="sidebar-text">Real-time Engine</span>
          </Link>

          <Link
            to="/dashboard/reports"
            className={`sidebar-link ${location.pathname === '/dashboard/reports' ? 'active' : ''}`}
            title="Compliance Reports"
          >
            <span className="sidebar-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            </span>
            <span className="sidebar-text">Compliance Reports</span>
          </Link>

          <Link
            to="/dashboard/models"
            className={`sidebar-link ${location.pathname === '/dashboard/models' ? 'active' : ''}`}
            title="Model Registry"
          >
            <span className="sidebar-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
            </span>
            <span className="sidebar-text">Model Registry</span>
          </Link>

          <span className="sidebar-nav-label" style={{ marginTop: '0.75rem' }}>Config</span>

          <Link
            to="/dashboard/settings"
            className={`sidebar-link ${location.pathname === '/dashboard/settings' ? 'active' : ''}`}
            title="Settings"
          >
            <span className="sidebar-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/><path d="M19.07 4.93L12 12M4.93 4.93L12 12"/></svg>
            </span>
            <span className="sidebar-text">Settings</span>
          </Link>
        </nav>

        {/* ── User Profile ─────────────────────────────────────── */}
        <div className="sidebar-footer">
          <div className="user-profile" onClick={handleLogout} title="Click to log out">
            <div className="avatar">{avatarLetter}</div>
            <div className="user-info">
              <span className="user-name">{displayName}</span>
              <span className="user-role">{displayRole}</span>
            </div>
          </div>
        </div>
      </aside>

      {/* ── Main Content ─────────────────────────────────────────── */}
      <main className="main-content">
        <header className="main-header">
          {headerContent}
        </header>

        <div className="content-container">
          {children}
        </div>
      </main>
    </div>
  );
}
