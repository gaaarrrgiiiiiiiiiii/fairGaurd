/**
 * App.tsx — FairGuard Dashboard
 *
 * Phase 3 wiring:
 *   • useSSE: real-time decision events (replaces mock DemoSimulator data)
 *   • useAnalytics: real DB stats (replaces client-side accumulators)
 *   • SSE connection status indicator in header
 *   • DemoSimulator still available for manual test submissions
 */
import { useCallback, useState } from 'react';
import DecisionFeed from './components/DecisionFeed';
import StatsOverview from './components/StatsOverview';
import BiasMetricsChart from './components/BiasMetricsChart';
import CausalGraph from './components/CausalGraph';
import DemoSimulator from './components/DemoSimulator';
import MetricsGaugePanel from './components/MetricsGaugePanel';
import { complianceReportUrl } from './services/api';
import { useSSE } from './hooks/useSSE';
import { useAnalytics } from './hooks/useAnalytics';
import type {
  DecisionRecord,
  GaugeMetrics,
  ChartDataPoint,
} from './types';

function App() {
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
    <div className="app-container">
      <header className="app-header">
        <div>
          <h1 className="logo-title">
            FAIR<span className="logo-accent">GUARD</span>
          </h1>
          <p className="logo-subtitle">
            AI Fairness Firewall —{' '}
            {latencyAvg > 0 ? (
              <>
                Intercepting Bias in{' '}
                <span className="logo-accent" style={{ fontFamily: 'var(--font-mono)' }}>
                  {latencyAvg}ms
                </span>
              </>
            ) : (
              'Real-time AI bias detection & correction'
            )}
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {/* SSE connection status indicator */}
          <span
            title={sseError ?? (connected ? 'Live stream connected' : 'Connecting…')}
            style={{
              display:       'inline-flex',
              alignItems:    'center',
              gap:           '0.35rem',
              fontSize:      '0.75rem',
              color:         connected ? 'var(--accent-green, #22c55e)' : 'var(--text-muted)',
              fontFamily:    'var(--font-mono)',
            }}
          >
            <span
              style={{
                width:        '8px',
                height:       '8px',
                borderRadius: '50%',
                background:   connected ? '#22c55e' : '#64748b',
                boxShadow:    connected ? '0 0 6px #22c55e' : 'none',
                animation:    connected ? 'pulse 2s infinite' : 'none',
              }}
            />
            {connected ? 'LIVE' : 'CONNECTING'}
          </span>

          <button className="pill-button">API Keys</button>
          <button
            className="pill-button"
            onClick={() => window.open(complianceReportUrl(), '_blank')}
          >
            Download Compliance Report
          </button>
        </div>
      </header>

      <StatsOverview
        total={stats.total}
        interventions={stats.interventions}
        complianceRate={stats.complianceRate}
      />
      <MetricsGaugePanel metrics={gaugeMetrics} />

      <div className="dashboard-grid">
        <div className="left-column">
          <BiasMetricsChart data={chartData} />
          <CausalGraph decision={decisions[0] ?? null} />
        </div>
        <div className="right-column">
          <DecisionFeed decisions={decisions} />
          <DemoSimulator onNewDecision={handleNewDecision} />
        </div>
      </div>
    </div>
  );
}

export default App;
