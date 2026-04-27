import React from 'react';
import type { DecisionRecord } from '../types';

interface Props {
  decision: DecisionRecord;
  onExpand?: (decision: DecisionRecord) => void;
}

const DecisionCard: React.FC<Props> = ({ decision, onExpand }) => {
  const isBiased = decision.bias_detected;

  const origConf = decision.original_decision?.confidence != null
    ? (decision.original_decision.confidence * 100).toFixed(1)
    : '0';
  const newConf = decision.corrected_decision?.confidence != null
    ? (decision.corrected_decision.confidence * 100).toFixed(1)
    : origConf;

  return (
    <div
      className={`decision-item ${isBiased ? 'biased' : ''}`}
      onClick={() => onExpand?.(decision)}
      style={{ cursor: onExpand ? 'pointer' : 'default' }}
    >
      <div className="decision-header">
        <div>
          <h3 className="decision-id">
            <span style={{ marginRight: '0.4rem', fontSize: '0.9rem' }}>
              {isBiased ? '⚠️' : '✅'}
            </span>
            Applicant #{decision.audit_id ? decision.audit_id.substring(0, 8) : 'Unknown'}
            {decision.latency != null && (
              <span style={{
                fontSize: '0.65rem',
                fontWeight: 400,
                color: 'var(--text-dim)',
                marginLeft: '0.5rem',
                fontFamily: 'var(--font-mono)',
              }}>
                ({decision.latency}ms)
              </span>
            )}
          </h3>
          <div style={{
            display: 'flex',
            gap: '0.75rem',
            marginTop: '0.5rem',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.82rem',
            flexWrap: 'wrap',
          }}>
            <div style={{
              padding: '0.4rem 0.75rem',
              backgroundColor: 'rgba(255,255,255,0.04)',
              borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.06)',
            }}>
              <span style={{ color: 'var(--text-dim)', fontSize: '0.7rem' }}>Original: </span>
              <span className={isBiased ? 'strike' : ''}>
                {decision.original_decision?.decision}
              </span>{' '}
              <span style={{ color: 'var(--text-dim)' }}>({origConf}%)</span>
            </div>
            {isBiased && (
              <div style={{
                padding: '0.4rem 0.75rem',
                backgroundColor: 'rgba(184, 242, 58, 0.06)',
                border: '1px solid rgba(184, 242, 58, 0.15)',
                borderRadius: '8px',
              }}>
                <span style={{ color: 'var(--text-dim)', fontSize: '0.7rem' }}>Corrected: </span>
                <span className="text-green">{decision.corrected_decision?.decision}</span>{' '}
                <span style={{ color: 'var(--text-dim)' }}>({newConf}%)</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {isBiased && (
        <div className="intervention-box">
          <strong>⚡ Intervention Triggered:</strong>
          <br />
          {decision.explanation}
        </div>
      )}
    </div>
  );
};

export default DecisionCard;
