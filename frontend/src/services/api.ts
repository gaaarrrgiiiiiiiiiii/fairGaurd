/**
 * FairGuard API client
 *
 * Phase 1 C1 fix: Removed hardcoded sk_fgt_12345.
 * Auth token is now read from VITE_API_TOKEN env var (set in .env).
 * Phase 3: Added streamDecisions (SSE) and getAnalytics().
 */
import axios, { AxiosError } from 'axios';
import type { DecisionRequestPayload, DecisionRecord, DriftStatus, StatsData } from '../types';

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

/**
 * Auth token priority:
 *   1. VITE_API_TOKEN env var (set in frontend/.env)
 *   2. VITE_DEV_MODE=true  → no auth (backend DEV_MODE must also be true)
 *
 * In production: set VITE_API_TOKEN to a valid JWT obtained from POST /v1/auth/token
 */
const API_TOKEN = import.meta.env.VITE_API_TOKEN ?? '';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10_000,
  headers: {
    'Content-Type': 'application/json',
    ...(API_TOKEN ? { Authorization: `Bearer ${API_TOKEN}` } : {}),
  },
});

// Normalise error messages
api.interceptors.response.use(
  (res) => res,
  (error: AxiosError) => {
    const message =
      (error.response?.data as { detail?: string })?.detail ??
      error.message ??
      'Unknown API error';
    return Promise.reject(new Error(message));
  },
);

// ---------------------------------------------------------------------------
// REST endpoints
// ---------------------------------------------------------------------------

/** Evaluate a single applicant decision for bias. */
export async function evaluateDecision(
  payload: DecisionRequestPayload,
): Promise<DecisionRecord> {
  const { data } = await api.post<DecisionRecord>('/v1/decision', payload);
  return data;
}

/** Check model drift status for the current tenant. */
export async function getDriftStatus(): Promise<DriftStatus> {
  const { data } = await api.get<DriftStatus>('/v1/drift/status');
  return data;
}

/** Return real-time aggregate stats from the audit log DB. */
export async function getAnalytics(): Promise<StatsData> {
  const { data } = await api.get<{
    total_decisions: number;
    interventions: number;
    compliance_rate: number;
  }>('/v1/stream/analytics');
  return {
    total: data.total_decisions,
    interventions: data.interventions,
    complianceRate: data.compliance_rate,
  };
}

/** Return the URL for downloading the compliance PDF. */
export function complianceReportUrl(): string {
  return `${BASE_URL}/v1/report/generate`;
}

// ---------------------------------------------------------------------------
// SSE — Real-time decision stream (Phase 3)
// ---------------------------------------------------------------------------

export interface SSEDecisionEvent {
  audit_id: string;
  original_decision: { decision: string; confidence: number };
  corrected_decision: { decision: string; confidence: number; correction_applied?: boolean; cf_method?: string };
  bias_detected: boolean;
  bias_scores: { DPD: number; EOD: number; ICD: number; CAS: number };
  explanation: string | null;
  protected_attributes: string[];
}

/**
 * Open an SSE connection to /v1/stream/decisions.
 * Returns an EventSource instance. Caller must call .close() on unmount.
 *
 * EventSource does not support custom headers natively.
 * Workaround: pass token as query param (backend reads ?token= as fallback)
 * OR use FAIRGUARD_DEV_MODE=true for local dev (no auth needed).
 */
export function streamDecisions(
  onEvent: (event: SSEDecisionEvent) => void,
  onError?: (err: Event) => void,
): EventSource {
  const url = new URL(`${BASE_URL}/v1/stream/decisions`);
  // Pass token as query param for EventSource (can't set headers)
  if (API_TOKEN) url.searchParams.set('token', API_TOKEN);

  const es = new EventSource(url.toString());

  es.addEventListener('decision', (e: MessageEvent) => {
    try {
      const data = JSON.parse(e.data) as SSEDecisionEvent;
      onEvent(data);
    } catch {
      // malformed event — ignore
    }
  });

  if (onError) es.onerror = onError;

  return es;
}

export default api;
