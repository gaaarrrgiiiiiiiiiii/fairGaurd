
import type { DecisionRecord } from '../types';

interface NodeProps {
  x: number; y: number;
  label: string; sublabel?: string;
  biased?: boolean; isTarget?: boolean; dimmed?: boolean;
}

function GraphNode({ x, y, label, sublabel, biased, isTarget, dimmed }: NodeProps) {
  const borderColor = biased ? '#ef4444' : isTarget ? '#CCFF00' : 'rgba(255,255,255,0.12)';
  const bgColor = biased
    ? 'rgba(239,68,68,0.12)'
    : isTarget
    ? 'rgba(204,255,0,0.1)'
    : 'rgba(255,255,255,0.04)';
  const textColor = biased ? '#ef4444' : isTarget ? '#CCFF00' : dimmed ? '#6b7280' : '#d1d5db';

  const W = isTarget ? 72 : 64;
  const H = isTarget ? 42 : 36;

  return (
    <g transform={`translate(${x},${y})`} style={{ transition: 'all 0.4s ease' }}>
      {/* Glow ring for active nodes */}
      {(biased || isTarget) && (
        <ellipse
          rx={W / 2 + 8} ry={H / 2 + 8}
          fill="none"
          stroke={biased ? 'rgba(239,68,68,0.15)' : 'rgba(204,255,0,0.12)'}
          strokeWidth="1"
          className={biased ? 'graph-node-pulse' : ''}
        />
      )}
      {/* Node box */}
      <rect
        x={-W / 2} y={-H / 2}
        width={W} height={H}
        rx={isTarget ? 10 : 8}
        fill={bgColor}
        stroke={borderColor}
        strokeWidth={biased || isTarget ? 1.5 : 1}
        opacity={dimmed ? 0.45 : 1}
      />
      <text
        textAnchor="middle"
        dy={sublabel ? '-2' : '4'}
        fontSize={isTarget ? 11 : 10}
        fontWeight={isTarget ? 700 : 600}
        fill={textColor}
        fontFamily="Inter, system-ui"
        opacity={dimmed ? 0.5 : 1}
      >
        {label}
      </text>
      {sublabel && (
        <text
          textAnchor="middle"
          dy="12"
          fontSize="8.5"
          fill={dimmed ? '#4b5563' : '#6b7280'}
          fontFamily="JetBrains Mono, monospace"
        >
          {sublabel}
        </text>
      )}
    </g>
  );
}

interface EdgeProps {
  x1: number; y1: number; x2: number; y2: number;
  active?: boolean; dimmed?: boolean; markerId: string;
}

function GraphEdge({ x1, y1, x2, y2, active, dimmed, markerId }: EdgeProps) {
  return (
    <line
      x1={x1} y1={y1} x2={x2} y2={y2}
      stroke={active ? '#ef4444' : dimmed ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.15)'}
      strokeWidth={active ? 2 : 1}
      strokeDasharray={active ? '6 3' : dimmed ? '2 4' : 'none'}
      markerEnd={`url(#${markerId})`}
      opacity={dimmed ? 0.3 : 1}
      style={{ transition: 'all 0.4s ease' }}
    />
  );
}

const CausalGraph = ({ decision }: { decision?: DecisionRecord | null }) => {
  const isBiased = decision?.bias_detected === true;

  let causedByAttr = 'Sex';
  if (decision?.explanation) {
    if (decision.explanation.toLowerCase().includes('race')) causedByAttr = 'Race';
    else if (decision.explanation.toLowerCase().includes('age')) causedByAttr = 'Age';
  }

  // Layout: 3 columns — inputs (x=80), mediators (x=230), output (x=390)
  const nodes = {
    protected: { x: 80,  y: 80,  label: causedByAttr, sublabel: 'Protected' },
    neutral:   { x: 80,  y: 170, label: 'Income',     sublabel: 'Feature' },
    neutral2:  { x: 80,  y: 260, label: 'Age / Exp',  sublabel: 'Feature' },
    domain:    { x: 230, y: 110, label: 'Domain',     sublabel: 'Mediator' },
    risk:      { x: 230, y: 220, label: 'Risk Score',  sublabel: 'Mediator' },
    decision:  { x: 390, y: 165, label: 'Decision',   sublabel: undefined },
  };

  return (
    <div className="card-wrapper" style={{ minHeight: '300px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{
            width: 3, height: 18, borderRadius: 2,
            background: isBiased ? '#ef4444' : '#CCFF00',
            display: 'inline-block',
            boxShadow: isBiased ? '0 0 6px rgba(239,68,68,0.6)' : '0 0 6px rgba(204,255,0,0.5)',
          }} />
          <h2 className="card-title" style={{ margin: 0 }}>Causal Graph Map</h2>
          <span style={{
            fontSize: '0.6rem', fontFamily: 'var(--font-mono)', color: '#4b5563',
            border: '1px solid rgba(255,255,255,0.08)', borderRadius: '4px',
            padding: '1px 5px', letterSpacing: '0.5px',
          }}>DoWhy</span>
        </div>

        {/* Status pill */}
        <span style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.3rem',
          padding: '0.25rem 0.65rem',
          borderRadius: '99px',
          fontSize: '0.7rem',
          fontFamily: 'var(--font-mono)',
          fontWeight: 600,
          background: isBiased ? 'rgba(239,68,68,0.1)' : 'rgba(204,255,0,0.08)',
          border: `1px solid ${isBiased ? 'rgba(239,68,68,0.25)' : 'rgba(204,255,0,0.2)'}`,
          color: isBiased ? '#f87171' : '#CCFF00',
        }}>
          <span style={{
            width: 6, height: 6, borderRadius: '50%',
            background: isBiased ? '#ef4444' : '#CCFF00',
            boxShadow: `0 0 4px ${isBiased ? '#ef4444' : '#CCFF00'}`,
            animation: isBiased ? 'pulse 1.5s infinite' : 'none',
          }} />
          {isBiased ? 'BIAS DETECTED' : 'COMPLIANT'}
        </span>
      </div>

      {/* SVG Graph */}
      <div style={{
        background: 'rgba(6,7,10,0.6)',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: '12px',
        padding: '1rem',
        overflow: 'hidden',
      }}>
        <svg viewBox="0 0 470 320" style={{ width: '100%', height: 'auto', overflow: 'visible' }}>
          <defs>
            <marker id="arrow-active" viewBox="0 0 10 10" refX="32" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
            </marker>
            <marker id="arrow-normal" viewBox="0 0 10 10" refX="32" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(255,255,255,0.2)" />
            </marker>
            <marker id="arrow-dim" viewBox="0 0 10 10" refX="32" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(255,255,255,0.08)" />
            </marker>
            <filter id="causal-glow">
              <feGaussianBlur stdDeviation="2" result="blur" />
              <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          </defs>

          {/* Column background lanes */}
          <rect x="44" y="20" width="72" height="270" rx="8" fill="rgba(255,255,255,0.015)" />
          <rect x="194" y="55" width="72" height="185" rx="8" fill="rgba(255,255,255,0.015)" />
          <rect x="354" y="125" width="72" height="80" rx="8" fill="rgba(255,255,255,0.015)" />

          {/* Column labels */}
          <text x="80" y="14" textAnchor="middle" fontSize="8" fill="rgba(255,255,255,0.2)" fontFamily="JetBrains Mono, monospace" letterSpacing="0.5">INPUT</text>
          <text x="230" y="48" textAnchor="middle" fontSize="8" fill="rgba(255,255,255,0.2)" fontFamily="JetBrains Mono, monospace" letterSpacing="0.5">MEDIATE</text>
          <text x="390" y="118" textAnchor="middle" fontSize="8" fill="rgba(255,255,255,0.2)" fontFamily="JetBrains Mono, monospace" letterSpacing="0.5">OUTPUT</text>

          {/* Edges */}
          <GraphEdge x1={112} y1={80}  x2={194} y2={110} active={isBiased} markerId={isBiased ? 'arrow-active' : 'arrow-normal'} />
          <GraphEdge x1={112} y1={80}  x2={194} y2={220} active={false}    markerId="arrow-dim" dimmed />
          <GraphEdge x1={112} y1={170} x2={194} y2={110} active={false}    markerId="arrow-normal" />
          <GraphEdge x1={112} y1={170} x2={194} y2={220} active={false}    markerId="arrow-normal" />
          <GraphEdge x1={112} y1={260} x2={194} y2={220} active={false}    markerId="arrow-normal" />
          <GraphEdge x1={266} y1={110} x2={354} y2={165} active={isBiased} markerId={isBiased ? 'arrow-active' : 'arrow-normal'} />
          <GraphEdge x1={266} y1={220} x2={354} y2={165} active={false}    markerId="arrow-normal" />

          {/* Nodes */}
          <GraphNode {...nodes.protected} biased={isBiased} />
          <GraphNode {...nodes.neutral} dimmed={!isBiased} />
          <GraphNode {...nodes.neutral2} dimmed={!isBiased} />
          <GraphNode {...nodes.domain} biased={isBiased} />
          <GraphNode {...nodes.risk} dimmed={!isBiased} />
          <GraphNode {...nodes.decision} isTarget />
        </svg>
      </div>

      {/* Footer */}
      <p style={{
        color: isBiased ? '#f87171' : 'var(--text-muted)',
        fontSize: '0.7rem',
        textAlign: 'center',
        marginTop: '0.75rem',
        fontFamily: 'var(--font-mono)',
        letterSpacing: '0.2px',
        opacity: 0.8,
      }}>
        {isBiased
          ? `⚠ Causal path: ${causedByAttr} → Domain → Decision — intervention triggered`
          : '✓ All causal paths within fairness thresholds — no intervention required'}
      </p>
    </div>
  );
};

export default CausalGraph;
