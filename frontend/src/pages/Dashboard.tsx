/**
 * Dashboard.tsx — FairGuard Dashboard
 */
import { useCallback, useState } from 'react';
import DecisionFeed from '../components/DecisionFeed';
import StatsOverview from '../components/StatsOverview';
import BiasMetricsChart from '../components/BiasMetricsChart';
import CausalGraph from '../components/CausalGraph';
import DemoSimulator from '../components/DemoSimulator';
import MetricsGaugePanel from '../components/MetricsGaugePanel';
import api, { complianceReportUrl } from '../services/api';
import { useSSE } from '../hooks/useSSE';
import { useAnalytics } from '../hooks/useAnalytics';
import DashboardLayout from '../layouts/DashboardLayout';
import type {
  DecisionRecord,
  GaugeMetrics,
  ChartDataPoint,
} from '../types';

function Dashboard() {
  // ── Real-time data ──────────────────────────────────────────────────────
  const { stats, refresh: refreshStats, setStats } = useAnalytics();

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
    (decision: DecisionRecord & { latency?: number; bias_scores?: any }) => {
      setDecisions((prev) => [decision, ...prev].slice(0, 50));
      if (decision.latency) {
        setLatencyAvg((prev) => Math.round((prev * 2 + decision.latency!) / 3));
      }

      // Update Gauge Metrics
      if (decision.bias_scores) {
        const gauge: GaugeMetrics = {
          dpd: decision.bias_scores.DPD || 0,
          eod: decision.bias_scores.EOD || 0,
          icd: decision.bias_scores.ICD || 0,
          cas: decision.bias_scores.CAS || 0,
        };
        setGaugeMetrics(gauge);
        
        const now = new Date();
        const ts  = `${now.getHours()}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
        const chartPoint: ChartDataPoint = {
          timestamp: ts,
          icd_score: gauge.icd,
          dpd_score: gauge.dpd,
        };
        setChartData((prev) => [...prev, chartPoint].slice(-10));
      }

      setStats((prev) => {
        const interventions = prev.interventions + (decision.bias_detected ? 1 : 0);
        const total = prev.total + 1;
        const complianceRate = total > 0 ? Math.round(((total - interventions) / total) * 100) : 100;
        return { total, interventions, complianceRate };
      });

      // Optionally refresh stats from DB
      refreshStats();
    },
    [refreshStats, setStats],
  );

  const { connected, error: sseError } = useSSE(handleStreamEvent);

  // ── Render ───────────────────────────────────────────────────────────────
  const headerContent = (
    <>
      <div className="header-title">
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Real-time Engine</h2>
        <p className="logo-subtitle" style={{ margin: 0, fontSize: '0.8rem' }}>
          {latencyAvg > 0 ? (
            <>
              Intercepting Bias in <span className="logo-accent" style={{ fontFamily: 'var(--font-mono)' }}>{latencyAvg}ms</span>
            </>
          ) : (
            'AI bias detection & correction'
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

        <button className="lp-btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}>API Keys</button>
        <button
          className="lp-btn-primary"
          style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
          onClick={async () => {
            try {
              const res = await api.get('/v1/report/generate', { responseType: 'blob' });
              const blob = new Blob([res.data], { type: 'application/pdf' });
              const url = window.URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.setAttribute('download', 'fairguard_compliance_report.pdf');
              document.body.appendChild(link);
              link.click();
              link.remove();
              setTimeout(() => window.URL.revokeObjectURL(url), 1000);
            } catch {
              // Fallback: open the report endpoint directly in a new tab
              window.open(complianceReportUrl(), '_blank');
            }
          }}
        >
          Download Report
        </button>
      </div>
    </>
  );

  return (
    <DashboardLayout headerContent={headerContent}>
      <StatsOverview
        total={stats.total}
        interventions={stats.interventions}
        complianceRate={stats.complianceRate}
        avgLatency={latencyAvg}
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
    </DashboardLayout>
  );
}

export default Dashboard;
