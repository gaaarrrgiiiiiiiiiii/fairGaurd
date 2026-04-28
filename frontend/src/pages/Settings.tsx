import DashboardLayout from '../layouts/DashboardLayout';

export default function Settings() {
  const headerContent = (
    <div className="header-title">
      <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Settings</h2>
      <p className="logo-subtitle" style={{ margin: 0, fontSize: '0.8rem' }}>Configure API keys and fairness thresholds</p>
    </div>
  );

  return (
    <DashboardLayout headerContent={headerContent}>
      <div className="glass-panel" style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
        <h3 style={{ fontSize: '1.5rem', marginBottom: '1.5rem', color: '#fff' }}>Platform Settings</h3>
        <p style={{ color: '#8b949e', marginBottom: '2rem' }}>This module is under construction. Use it to configure API keys, webhook URLs, and fairness thresholds.</p>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <label style={{ display: 'block', color: '#8b949e', marginBottom: '0.5rem' }}>API Key</label>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <input type="text" value="sk_fgt_****************" readOnly style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', padding: '0.75rem', borderRadius: '6px' }} />
              <button className="lp-btn-ghost">Copy</button>
            </div>
          </div>
          
          <div>
            <label style={{ display: 'block', color: '#8b949e', marginBottom: '0.5rem' }}>Webhook URL</label>
            <input type="text" placeholder="https://api.yourcompany.com/fairness-webhook" style={{ width: '100%', backgroundColor: 'rgba(0,0,0,0.5)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', padding: '0.75rem', borderRadius: '6px' }} />
          </div>
          
          <div>
            <label style={{ display: 'block', color: '#8b949e', marginBottom: '0.5rem' }}>Strictness Level</label>
            <select style={{ width: '100%', backgroundColor: 'rgba(0,0,0,0.5)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', padding: '0.75rem', borderRadius: '6px', appearance: 'none' }}>
              <option>Moderate (Recommend corrections)</option>
              <option>Strict (Auto-correct bias)</option>
              <option>Lenient (Log only)</option>
            </select>
          </div>
          
          <div style={{ marginTop: '1rem' }}>
            <button className="lp-btn-primary">Save Changes</button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
