import React from 'react';
import type { GaugeMetrics } from '../types';

interface Props {
  metrics: GaugeMetrics;
}

const GAUGES: { label: string; key: keyof GaugeMetrics; max: number }[] = [
  { label: 'DPD (Parity)',            key: 'dpd', max: 0.3 },
  { label: 'EOD (Opportunity)',       key: 'eod', max: 0.3 },
  { label: 'ICD (Counterfactual)',    key: 'icd', max: 0.3 },
  { label: 'CAS (Causal Attribution)',key: 'cas', max: 0.3 },
];

const WARN_THRESHOLD = 0.15;

const getColor = (val: number): string => {
  if (val > WARN_THRESHOLD + 0.05) return 'var(--accent-red)';
  if (val > WARN_THRESHOLD)        return 'var(--accent-yellow)';
  return 'var(--accent-green)';
};

const MetricsGaugePanel: React.FC<Props> = ({ metrics }) => (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
    {GAUGES.map(({ label, key, max }) => {
      const val   = metrics[key];
      const pct   = Math.min((val / max) * 100, 100);
      const color = getColor(val);
      return (
        <div key={key} className="card-wrapper" style={{ padding: '1rem', alignItems: 'center' }}>
          <h4 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>
            {label}
          </h4>
          <div style={{ fontSize: '1.5rem', fontFamily: 'var(--font-mono)', fontWeight: 'bold', color }}>
            {(val * 100).toFixed(1)}%
          </div>
          <div style={{ width: '100%', height: '6px', backgroundColor: '#2a364a', borderRadius: '3px', marginTop: '0.5rem', overflow: 'hidden' }}>
            <div style={{ width: `${pct}%`, height: '100%', backgroundColor: color, transition: 'width 0.5s ease-out' }} />
          </div>
        </div>
      );
    })}
  </div>
);

export default MetricsGaugePanel;
