import React from 'react';
import DecisionCard from './DecisionCard';

const DecisionFeed = ({ decisions }) => {
  return (
    <div className="card-wrapper feed-container">
      <h2 className="card-title">Live Decision Firewall</h2>
      <div className="feed-list">
        {decisions.length === 0 ? (
          <div style={{color: 'var(--text-muted)', textAlign: 'center', marginTop: '4rem'}}>Awaiting traffic...</div>
        ) : (
          decisions.map((d, index) => (
            <DecisionCard key={index} decision={d} onExpand={() => console.log('Expand', d)} />
          ))
        )}
      </div>
    </div>
  );
};

export default DecisionFeed;
