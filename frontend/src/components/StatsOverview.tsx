import React from 'react';

const StatsOverview = ({ total, interventions, complianceRate }) => {
  return (
    <div className="stats-grid">
      <div className="stat-card">
        <h3 className="stat-label">Decisions Evaluated</h3>
        <p className="stat-value">{total.toLocaleString()}</p>
      </div>
      <div className="stat-card yellow">
        <h3 className="stat-label">Interventions Triggered</h3>
        <p className="stat-value">{interventions.toLocaleString()}</p>
      </div>
      <div className="stat-card green">
        <h3 className="stat-label">Pipeline Compliance</h3>
        <p className="stat-value">{complianceRate}%</p>
      </div>
    </div>
  );
};

export default StatsOverview;
