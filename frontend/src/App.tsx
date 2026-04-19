import { useState, useEffect } from 'react'
import DecisionFeed from './components/DecisionFeed'
import StatsOverview from './components/StatsOverview'
import BiasMetricsChart from './components/BiasMetricsChart'
import CausalGraph from './components/CausalGraph'
import DemoSimulator from './components/DemoSimulator'
import MetricsGaugePanel from './components/MetricsGaugePanel'

function App() {
  const [decisions, setDecisions] = useState([])
  const [stats, setStats] = useState({ total: 0, interventions: 0, complianceRate: 100 })
  const [latencyAvg, setLatencyAvg] = useState(214) // Initial optimistic latency
  const [gaugeMetrics, setGaugeMetrics] = useState({ dpd: 0.18, eod: 0.12, icd: 0.05, cas: 0.06 })
  const [chartData, setChartData] = useState([
    { timestamp: '12:00', icd_score: 0.05, dpd_score: 0.18 },
    { timestamp: '12:05', icd_score: 0.06, dpd_score: 0.18 },
    { timestamp: '12:10', icd_score: 0.05, dpd_score: 0.18 }
  ])

  const handleNewDecision = (decision) => {
    setDecisions(prev => [decision, ...prev].slice(0, 50));
    
    if (decision.latency) {
      setLatencyAvg(prev => Math.round((prev * 2 + decision.latency) / 3));
    }
    
    setStats(prev => {
      const newTotal = prev.total + 1;
      const newInterventions = prev.interventions + (decision.bias_detected ? 1 : 0);
      return {
        total: newTotal,
        interventions: newInterventions,
        complianceRate: Math.round(((newTotal - newInterventions) / newTotal) * 100 * 10) / 10
      }
    });

    const now = new Date();
    const timeStr = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
    
    setChartData(prev => {
      const newIcd = decision.bias_detected ? 0.20 : Math.random() * 0.08 + 0.02;
      
      setGaugeMetrics(g => ({
        ...g,
        icd: newIcd,
        cas: newIcd * 1.25 // Simulated proportional to ICD for real-time tracking
      }));
      
      const newData = [...prev, {
        timestamp: timeStr,
        icd_score: newIcd,
        dpd_score: decision.bias_detected ? Math.random() * 0.1 + 0.08 : 0.18
      }];
      return newData.slice(newData.length > 10 ? newData.length - 10 : 0);
    });
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div>
          <h1 className="logo-title">FAIR<span className="logo-accent">GUARD</span></h1>
          <p className="logo-subtitle">AI Fairness Firewall  —  Intercepting Bias in <span className="logo-accent" style={{fontFamily: 'var(--font-mono)'}}>{latencyAvg}ms</span></p>
        </div>
        <div>
          <button className="pill-button">API Keys</button>
          <button 
            className="pill-button" 
            onClick={() => window.open('http://localhost:8000/v1/report/generate', '_blank')}
          >
            Download Compliance Report
          </button>
        </div>
      </header>

      <StatsOverview total={stats.total} interventions={stats.interventions} complianceRate={stats.complianceRate} />
      <MetricsGaugePanel metrics={gaugeMetrics} />

      <div className="dashboard-grid">
        <div className="left-column">
          <BiasMetricsChart data={chartData} />
          <CausalGraph decision={decisions[0] || null} />
        </div>
        <div className="right-column">
          <DecisionFeed decisions={decisions} />
          <DemoSimulator onNewDecision={handleNewDecision} />
        </div>
      </div>
    </div>
  )
}

export default App
