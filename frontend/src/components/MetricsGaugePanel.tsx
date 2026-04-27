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

const getRawColor = (val: number): string => {
  if (val > WARN_THRESHOLD + 0.05) return '#ef4444';
  if (val > WARN_THRESHOLD)        return '#f59e0b';
  return '#10b981';
};

// Arc gauge SVG math
const ARC_RADIUS = 35;
const ARC_CENTER_X = 45;
const ARC_CENTER_Y = 48;
const ARC_START_ANGLE = -210;
const ARC_END_ANGLE = 30;
const ARC_TOTAL = ARC_END_ANGLE - ARC_START_ANGLE;

function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function describeArc(cx: number, cy: number, r: number, startAngle: number, endAngle: number) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const largeArc = endAngle - startAngle > 180 ? 1 : 0;
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 0 ${end.x} ${end.y}`;
}

const MetricsGaugePanel: React.FC<Props> = ({ metrics }) => (
  <div className="gauge-grid">
    {GAUGES.map(({ label, key, max }) => {
      const val   = metrics[key];
      const pct   = Math.min(val / max, 1);
      const color = getColor(val);
      const rawColor = getRawColor(val);

      const trackPath = describeArc(ARC_CENTER_X, ARC_CENTER_Y, ARC_RADIUS, ARC_START_ANGLE, ARC_END_ANGLE);
      const fillAngle = ARC_START_ANGLE + ARC_TOTAL * pct;
      const fillPath  = describeArc(ARC_CENTER_X, ARC_CENTER_Y, ARC_RADIUS, ARC_START_ANGLE, fillAngle);

      // Compute stroke lengths for animation
      const trackLen = (ARC_TOTAL / 360) * 2 * Math.PI * ARC_RADIUS;
      const fillLen  = trackLen * pct;

      return (
        <div key={key} className="gauge-card">
          <h4 className="gauge-label">{label}</h4>
          <svg className="gauge-svg" viewBox="0 0 90 58">
            <defs>
              <filter id={`glow-${key}`}>
                <feGaussianBlur stdDeviation="2" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            <path d={trackPath} className="gauge-track" />
            {pct > 0 && (
              <path
                d={fillPath}
                className="gauge-fill"
                stroke={rawColor}
                strokeDasharray={`${fillLen} ${trackLen}`}
                strokeDashoffset="0"
                filter={`url(#glow-${key})`}
              />
            )}
          </svg>
          <div className="gauge-value" style={{ color }}>{(val * 100).toFixed(1)}%</div>
        </div>
      );
    })}
  </div>
);

export default MetricsGaugePanel;
