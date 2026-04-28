import DashboardLayout from '../layouts/DashboardLayout';

export default function Reports() {
  const headerContent = (
    <div className="header-title">
      <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Compliance Reports</h2>
      <p className="logo-subtitle" style={{ margin: 0, fontSize: '0.8rem' }}>Generate and view audit reports</p>
    </div>
  );

  return (
    <DashboardLayout headerContent={headerContent}>
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <div>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: '#fff' }}>Compliance Reports</h3>
            <p style={{ color: '#8b949e' }}>This module is under construction. Future updates will include PDF report generation, historical audits, and regulatory compliance checks.</p>
          </div>
          <button className="lp-btn-primary">Generate New Report</button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="glass-panel" style={{ padding: '1rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div>
              <h4 style={{ color: '#fff', marginBottom: '0.25rem' }}>Q1 2026 Fairness Audit</h4>
              <p style={{ fontSize: '0.875rem', color: '#8b949e' }}>Generated on April 15, 2026</p>
            </div>
            <button className="lp-btn-ghost">Download PDF</button>
          </div>
          <div className="glass-panel" style={{ padding: '1rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div>
              <h4 style={{ color: '#fff', marginBottom: '0.25rem' }}>Monthly Compliance Check - March</h4>
              <p style={{ fontSize: '0.875rem', color: '#8b949e' }}>Generated on April 1, 2026</p>
            </div>
            <button className="lp-btn-ghost">Download PDF</button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
