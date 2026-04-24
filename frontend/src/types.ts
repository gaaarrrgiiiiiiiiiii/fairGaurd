// ============================================================
// FairGuard Frontend Type Definitions
// ============================================================

export interface ModelOutput {
  decision: string;
  confidence: number;
  correction_applied?: boolean;
}

export interface DecisionRecord {
  audit_id: string;
  original_decision: ModelOutput;
  corrected_decision: ModelOutput;
  bias_detected: boolean;
  explanation: string | null;
  latency?: number;  // ms, measured client-side
}

export interface BiasScores {
  DPD: number;  // Demographic Parity Difference
  EOD: number;  // Equalized Odds Difference
  ICD: number;  // Individual Counterfactual Disparity
  CAS: number;  // Causal Attribution Score
}

export interface GaugeMetrics {
  dpd: number;
  eod: number;
  icd: number;
  cas: number;
}

export interface ChartDataPoint {
  timestamp: string;
  icd_score: number;
  dpd_score: number;
}

export interface StatsData {
  total: number;
  interventions: number;
  complianceRate: number;
}

export interface DriftStatus {
  drift_detected: boolean;
  ks_statistic?: number;
  p_value?: number;
  message: string;
  recent_sample_size?: number;
  reference_sample_size?: number;
}

export interface ApplicantFeatures {
  age: number;
  income: number;
  sex: 'Male' | 'Female';
  [key: string]: unknown;
}

export interface DecisionRequestPayload {
  applicant_features: ApplicantFeatures;
  model_output: Omit<ModelOutput, 'correction_applied'>;
  protected_attributes: string[];
}

export interface TestCase {
  name: string;
  age: number;
  income: number;
  sex: 'Male' | 'Female';
  expectedOrig: string;
  attr: string;
}
