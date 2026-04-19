import React from 'react';

const MetricsGaugePanel = ({ metrics }) => {
  // metrics = { dpd: 0.18, eod: 0.12, icd: 0.05, cas: 0.06 }
  
  const threshold = 0.15; // Warning threshold
  
  const getStatusColor = (val) => {
    if (val > threshold + 0.05) return 'var(--accent-red)';
    if (val > threshold) return 'var(--accent-yellow)';
    return 'var(--accent-green)';
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
      {[
        { label: "DPD (Parity)", val: metrics.dpd, max: 0.3 },
        { label: "EOD (Opportunity)", val: metrics.eod, max: 0.3 },
        { label: "ICD (Counterfactual)", val: metrics.icd, max: 0.3 },
        { label: "CAS (Causal Attribution)", val: metrics.cas, max: 0.3 }
      ].map((item, idx) => {
        const pct = Math.min((item.val / item.max) * 100, 100);
        const color = getStatusColor(item.val);
        return (
          <div key={idx} className="card-wrapper" style={{ padding: '1rem', alignItems: 'center' }}>
            <h4 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>{item.label}</h4>
            <div style={{ fontSize: '1.5rem', fontFamily: 'var(--font-mono)', fontWeight: 'bold', color: color }}>
              {(item.val * 100).toFixed(1)}%
            </div>
            <div style={{ width: '100%', height: '6px', backgroundColor: '#2a364a', borderRadius: '3px', marginTop: '0.5rem', overflow: 'hidden' }}>
              <div style={{ width: `${pct}%`, height: '100%', backgroundColor: color, transition: 'width 0.5s ease-out' }}></div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default MetricsGaugePanel;
