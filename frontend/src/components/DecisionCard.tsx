import React from 'react';

const DecisionCard = ({ decision, onExpand }) => {
  const isBiased = decision.bias_detected;
  
  const origConf = decision.original_decision?.confidence ? (decision.original_decision.confidence * 100).toFixed(1) : '0';
  const newConf = decision.corrected_decision?.confidence ? (decision.corrected_decision.confidence * 100).toFixed(1) : origConf;
  
  return (
    <div className={`decision-item ${isBiased ? 'biased' : ''}`}>
      <div className="decision-header">
        <div>
          <h3 className="decision-id">
            Applicant #{decision.audit_id ? decision.audit_id.substring(0, 8) : 'Unknown'}
          </h3>
          <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem', fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
             <div style={{ padding: '0.5rem', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '4px'}}>
               <span style={{color: 'var(--text-muted)'}}>Original:</span> <span className={isBiased ? 'strike' : ''}>{decision.original_decision?.decision}</span> ({origConf}%)
             </div>
             {isBiased && (
               <div style={{ padding: '0.5rem', backgroundColor: 'rgba(184, 242, 58, 0.1)', border: '1px solid var(--accent-lime)', borderRadius: '4px'}}>
                 <span style={{color: 'var(--text-muted)'}}>Corrected:</span> <span className="text-green">{decision.corrected_decision?.decision}</span> ({newConf}%)
               </div>
             )}
          </div>
        </div>
      </div>
      
      {isBiased && (
        <div className="intervention-box">
          <strong>Intervention Triggered:</strong><br/>
          {decision.explanation}
        </div>
      )}
    </div>
  );
};

export default DecisionCard;
