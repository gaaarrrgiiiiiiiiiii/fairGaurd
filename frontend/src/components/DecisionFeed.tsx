import React from 'react';
import DecisionCard from './DecisionCard';
import type { DecisionRecord } from '../types';

interface Props {
  decisions: DecisionRecord[];
}

const DecisionFeed: React.FC<Props> = ({ decisions }) => (
  <div className="card-wrapper feed-container">
    <h2 className="card-title">Live Decision Firewall</h2>
    <div className="feed-list">
      {decisions.length === 0 ? (
        <div style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '4rem' }}>
          Awaiting traffic…
        </div>
      ) : (
        decisions.map((d) => (
          <DecisionCard key={d.audit_id} decision={d} />
        ))
      )}
    </div>
  </div>
);

export default DecisionFeed;
