import axios, { AxiosError } from 'axios';
import type { DecisionRequestPayload, DecisionRecord, DriftStatus } from '../types';

// ---------------------------------------------------------------------------
// Base URL — reads from Vite env variable, falls back to localhost
// ---------------------------------------------------------------------------
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10_000,
  headers: {
    'Content-Type': 'application/json',
    // Demo API key — in production, users inject their own
    Authorization: 'Bearer sk_fgt_12345',
  },
});

// ---------------------------------------------------------------------------
// Response interceptor — normalise error messages
// ---------------------------------------------------------------------------
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
// API functions
// ---------------------------------------------------------------------------

/** Evaluate a single applicant decision for bias. */
export async function evaluateDecision(
  payload: DecisionRequestPayload,
): Promise<DecisionRecord> {
  const { data } = await api.post<DecisionRecord>('/v1/decision', payload);
  return data;
}

/** Check model drift status for a tenant. */
export async function getDriftStatus(
  tenantId = 'tenant_local_dev',
): Promise<DriftStatus> {
  const { data } = await api.get<DriftStatus>('/v1/drift/status', {
    params: { tenant_id: tenantId },
  });
  return data;
}

/** Return the URL for downloading the compliance PDF. */
export function complianceReportUrl(tenantId = 'tenant_local_dev'): string {
  return `${BASE_URL}/v1/report/generate?tenant_id=${tenantId}`;
}

export default api;
