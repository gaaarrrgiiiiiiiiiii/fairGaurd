/**
 * useSSE — subscribes to the FairGuard real-time decision stream.
 *
 * Phase 3: Replaces mock data generation in DemoSimulator with
 * actual server-sent events from the audit log pipeline.
 *
 * Usage:
 *   const { connected, error } = useSSE(onNewDecision);
 */
import { useEffect, useRef, useState } from 'react';
import { streamDecisions, type SSEDecisionEvent } from '../services/api';
import type { DecisionRecord, GaugeMetrics, ChartDataPoint } from '../types';

export interface UseSSEResult {
  connected: boolean;
  error: string | null;
}

export function useSSE(
  onEvent: (decision: DecisionRecord, gaugeMetrics: GaugeMetrics, chartPoint: ChartDataPoint) => void,
): UseSSEResult {
  const [connected, setConnected]   = useState(false);
  const [error, setError]           = useState<string | null>(null);
  const esRef                       = useRef<EventSource | null>(null);

  useEffect(() => {
    const es = streamDecisions(
      (raw: SSEDecisionEvent) => {
        setConnected(true);
        setError(null);

        // Map SSE payload → DecisionRecord (matches existing component types)
        const decision: DecisionRecord = {
          audit_id:           raw.audit_id,
          original_decision:  raw.original_decision as DecisionRecord['original_decision'],
          corrected_decision: raw.corrected_decision as DecisionRecord['corrected_decision'],
          bias_detected:      raw.bias_detected,
          explanation:        raw.explanation,
        };

        // Derive gauge metrics from real bias scores
        const scores = raw.bias_scores ?? { DPD: 0, EOD: 0, ICD: 0, CAS: 0 };
        const gaugeMetrics: GaugeMetrics = {
          dpd: scores.DPD,
          eod: scores.EOD,
          icd: scores.ICD,
          cas: scores.CAS,
        };

        // Chart point with timestamp
        const now = new Date();
        const ts  = `${now.getHours()}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
        const chartPoint: ChartDataPoint = {
          timestamp: ts,
          icd_score: scores.ICD,
          dpd_score: scores.DPD,
        };

        onEvent(decision, gaugeMetrics, chartPoint);
      },
      () => {
        setConnected(false);
        setError('Stream disconnected — retrying…');
      },
    );

    esRef.current = es;

    es.onopen = () => {
      setConnected(true);
      setError(null);
    };

    return () => {
      es.close();
      esRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // mount/unmount only — onEvent is stable via useCallback in caller

  return { connected, error };
}
