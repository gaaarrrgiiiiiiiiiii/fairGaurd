import React from 'react';
import type { StatsData } from '../types';

const StatsOverview: React.FC<StatsData> = ({ total, interventions, complianceRate, avgLatency = 0 }) => (
  <div className="stats-grid">
    <div className="stat-card sf-dark-card">
      <h3 className="stat-label">Decisions Evaluated</h3>
      <p className="stat-value">{total.toLocaleString()}</p>
    </div>
    
    <div className="stat-card sf-dark-card">
      <h3 className="stat-label">Interventions Triggered</h3>
      <p className="stat-value">{interventions.toLocaleString()}</p>
    </div>
    
    <div className="stat-card sf-dark-card">
      <h3 className="stat-label">Average Latency</h3>
      <p className="stat-value">{avgLatency} <span style={{fontSize: '1rem', fontWeight: 500, color: '#8892B0'}}>ms</span></p>
    </div>
    
    <div className="stat-card sf-lime-card">
      <h3 className="stat-label">Pipeline Compliance</h3>
      <p className="stat-value">{complianceRate}%</p>
      <div className="sf-status-pill">Active</div>
    </div>
  </div>
);

export default StatsOverview;
