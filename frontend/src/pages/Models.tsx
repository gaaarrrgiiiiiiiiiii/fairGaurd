import DashboardLayout from '../layouts/DashboardLayout';

export default function Models() {
  const headerContent = (
    <div className="header-title">
      <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Model Registry</h2>
      <p className="logo-subtitle" style={{ margin: 0, fontSize: '0.8rem' }}>Manage your registered AI models</p>
    </div>
  );

  return (
    <DashboardLayout headerContent={headerContent}>
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: '#fff' }}>Model Registry</h3>
        <p style={{ color: '#8b949e', marginBottom: '2rem' }}>This module is under construction. It will display a list of all registered AI models, their status, and compliance scores.</p>
        
        <div style={{ display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' }}>
          <div className="glass-panel" style={{ padding: '1.5rem', border: '1px solid rgba(255,255,255,0.05)' }}>
            <h4 style={{ color: '#CCFF00', marginBottom: '0.5rem' }}>HR Screening Model v2</h4>
            <p style={{ fontSize: '0.875rem', color: '#8b949e', marginBottom: '1rem' }}>Last audited: 2 hours ago</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.875rem', color: '#fff' }}>Status: <span style={{ color: '#22c55e' }}>Active</span></span>
              <button className="lp-btn-ghost" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}>View Details</button>
            </div>
          </div>
          <div className="glass-panel" style={{ padding: '1.5rem', border: '1px solid rgba(255,255,255,0.05)' }}>
            <h4 style={{ color: '#CCFF00', marginBottom: '0.5rem' }}>Credit Scoring Model v1</h4>
            <p style={{ fontSize: '0.875rem', color: '#8b949e', marginBottom: '1rem' }}>Last audited: 1 day ago</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.875rem', color: '#fff' }}>Status: <span style={{ color: '#eab308' }}>Needs Review</span></span>
              <button className="lp-btn-ghost" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}>View Details</button>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
