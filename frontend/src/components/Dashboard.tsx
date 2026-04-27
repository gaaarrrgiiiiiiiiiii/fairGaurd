/**
 * Dashboard.tsx — FairGuard Dashboard
 *
 * Phase 3 wiring:
 *   • useSSE: real-time decision events (replaces mock DemoSimulator data)
 *   • useAnalytics: real DB stats (replaces client-side accumulators)
 *   • SSE connection status indicator in header
 *   • DemoSimulator still available for manual test submissions
 */
import { useCallback, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';
import DecisionFeed from './DecisionFeed';
import StatsOverview from './StatsOverview';
import BiasMetricsChart from './BiasMetricsChart';
import CausalGraph from './CausalGraph';
import DemoSimulator from './DemoSimulator';
import MetricsGaugePanel from './MetricsGaugePanel';
import { complianceReportUrl } from '../services/api';
import { useSSE } from '../hooks/useSSE';
import { useAnalytics } from '../hooks/useAnalytics';
import type {
  DecisionRecord,
  GaugeMetrics,
  ChartDataPoint,
} from '../types';

/** Inline Face Scan SVG Animation — security guardian motif */
function FaceScanAnimation() {
  return (
    <div className="face-scan-container">
      <svg className="face-scan-svg" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="scanGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgba(184, 242, 58, 0)" />
            <stop offset="50%" stopColor="rgba(184, 242, 58, 0.3)" />
            <stop offset="100%" stopColor="rgba(184, 242, 58, 0)" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Outer rotating ring */}
        <circle className="face-scan-ring" cx="40" cy="40" r="38" />
        {/* Inner counter-rotating ring */}
        <circle className="face-scan-ring-inner" cx="40" cy="40" r="34" />

        {/* Corner brackets */}
        <g className="face-scan-corners" filter="url(#glow)">
          <line x1="12" y1="16" x2="12" y2="22" />
          <line x1="12" y1="16" x2="18" y2="16" />
          <line x1="68" y1="16" x2="68" y2="22" />
          <line x1="68" y1="16" x2="62" y2="16" />
          <line x1="12" y1="64" x2="12" y2="58" />
          <line x1="12" y1="64" x2="18" y2="64" />
          <line x1="68" y1="64" x2="68" y2="58" />
          <line x1="68" y1="64" x2="62" y2="64" />
        </g>

        {/* Face outline */}
        <g filter="url(#glow)">
          {/* Head oval */}
          <ellipse className="face-scan-outline" cx="40" cy="37" rx="13" ry="16" />
          {/* Eyes */}
          <ellipse className="face-scan-outline" cx="34" cy="34" rx="3" ry="1.8" />
          <ellipse className="face-scan-outline" cx="46" cy="34" rx="3" ry="1.8" />
          {/* Nose */}
          <line className="face-scan-outline" x1="40" y1="36" x2="40" y2="40" />
          {/* Mouth */}
          <path className="face-scan-outline" d="M 35 44 Q 40 47 45 44" />
          {/* Shoulders */}
          <path className="face-scan-outline" d="M 27 53 Q 27 57 32 60 L 40 62 L 48 60 Q 53 57 53 53" />
        </g>

        {/* Scanning beam */}
        <rect className="face-scan-beam" x="20" y="30" width="40" height="6" rx="3" />

        {/* Indicator dots */}
        <circle className="face-scan-dot" cx="40" cy="12" r="1.5" />
        <circle className="face-scan-dot" cx="66" cy="40" r="1.5" />
        <circle className="face-scan-dot" cx="40" cy="68" r="1.5" />
        <circle className="face-scan-dot" cx="14" cy="40" r="1.5" />
      </svg>
      <div className="face-scan-label">GUARDING</div>
    </div>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();

  // ── Real-time data ──────────────────────────────────────────────────────
  const { stats, refresh: refreshStats } = useAnalytics();

  const [decisions, setDecisions]       = useState<DecisionRecord[]>([]);
  const [latencyAvg, setLatencyAvg]     = useState<number>(0);
  const [gaugeMetrics, setGaugeMetrics] = useState<GaugeMetrics>({ dpd: 0, eod: 0, icd: 0, cas: 0 });
  const [chartData, setChartData]       = useState<ChartDataPoint[]>([]);

  // Stable callback — useSSE only mounts EventSource once
  const handleStreamEvent = useCallback(
    (decision: DecisionRecord, gauge: GaugeMetrics, chartPoint: ChartDataPoint) => {
      setDecisions((prev) => [decision, ...prev].slice(0, 50));
      setGaugeMetrics(gauge);
      setChartData((prev) => [...prev, chartPoint].slice(-10));
      // Refresh DB stats after each decision (debounced to at most once per 30s by hook)
      refreshStats();
    },
    [refreshStats],
  );

  // Manual simulator submissions (still useful for live demos)
  const handleNewDecision = useCallback(
    (decision: DecisionRecord & { latency?: number }) => {
      setDecisions((prev) => [decision, ...prev].slice(0, 50));
      if (decision.latency) {
        setLatencyAvg((prev) => Math.round((prev * 2 + decision.latency!) / 3));
      }
    },
    [],
  );

  const { connected, error: sseError } = useSSE(handleStreamEvent);

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <div className="sf-app-root">
      
      {/* ─── SALESFORCE STYLE TOP NAVIGATION ────────────────────── */}
      <nav className="sf-top-nav">
        <div className="sf-nav-logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
          FAIR<span>GUARD</span>
        </div>
        
        <div className="sf-nav-pill">
          <button className="sf-nav-item active">Dashboard</button>
          <button className="sf-nav-item">Decisions</button>
          <button className="sf-nav-item">Interventions</button>
          <button className="sf-nav-item">Policies</button>
        </div>
        
        <div className="sf-nav-actions">
          <span
            className={`sse-status ${connected ? 'connected' : 'disconnected'}`}
            title={sseError ?? (connected ? 'Live stream connected' : 'Connecting…')}
          >
            <span className={`sse-dot ${connected ? 'live' : 'offline'}`} />
            {connected ? 'LIVE' : 'CONNECTING'}
          </span>
          <button className="sf-download-btn" onClick={() => window.open(complianceReportUrl(), '_blank')}>
            Compliance Report
          </button>
          <div className="sf-avatar-placeholder">🛡️</div>
        </div>
      </nav>

      {/* ─── PAGE TITLE ─────────────────────────────────────────── */}
      <div className="sf-page-header">
        <div className="sf-page-title-row">
          <FaceScanAnimation />
          <h1 className="sf-page-title">Fairness Overview</h1>
        </div>
      </div>

      {/* ─── TOP METRICS DOCK (Dark Mode) ─────────────────────── */}
      <div className="sf-metrics-dock">
        <StatsOverview
          total={stats.total}
          interventions={stats.interventions}
          complianceRate={stats.complianceRate}
          avgLatency={latencyAvg}
        />
        
        {/* Timeline Chart spans below the 3 left stats */}
        <div className="sf-timeline-wrapper">
          <BiasMetricsChart data={chartData} />
        </div>
      </div>

      {/* ─── BOTTOM SPLIT PANEL (White / Light Mode) ────────────── */}
      <div className="sf-white-container">
        
        {/* Gauges act as the 'Active Filters' bar */}
        <div className="sf-filters-bar">
          <div className="sf-filters-label">Active Thresholds:</div>
          <div className="sf-gauges-inline">
            <MetricsGaugePanel metrics={gaugeMetrics} />
          </div>
        </div>

        <div className="sf-split-layout">
          
          {/* Left: Feed List (Light UI) */}
          <div className="sf-split-left">
            <h3 className="sf-panel-title">Recent Decisions</h3>
            <div className="sf-feed-wrapper">
              <DecisionFeed decisions={decisions} />
            </div>
          </div>
          
          {/* Right: Detail View (Nested Dark UI) */}
          <div className="sf-split-right">
            <div className="sf-detail-card">
              <div className="sf-detail-header">
                <h3>Decision Details</h3>
                <span className="sf-detail-badge">Audit View</span>
              </div>
              <div className="sf-detail-body">
                <CausalGraph decision={decisions[0] ?? null} />
                <div style={{ marginTop: '2rem' }}>
                  <DemoSimulator onNewDecision={handleNewDecision} />
                </div>
              </div>
            </div>
          </div>
          
        </div>
      </div>

    </div>
  );
}
