import React from 'react';
import DecisionCard from './DecisionCard';
import type { DecisionRecord } from '../types';

interface Props {
  decisions: DecisionRecord[];
}

const DecisionFeed: React.FC<Props> = ({ decisions }) => (
  <div className="feed-container sf-clean-feed">
    <div className="feed-list">
      {decisions.length === 0 ? (
        <div className="feed-empty sf-feed-empty">
          <div className="feed-empty-icon" style={{ opacity: 0.2 }}>🛡️</div>
          <div className="sf-empty-title">
            Awaiting traffic…
          </div>
          <div className="sf-empty-sub">
            Run the simulator to fire test decisions through the firewall
          </div>
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
