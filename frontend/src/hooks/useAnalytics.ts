/**
 * useAnalytics — polls /v1/stream/analytics for real DB stats.
 *
 * Phase 3: Replaces the client-side counter accumulation in App.tsx
 * with authoritative numbers from the database.
 * Polls every 30 s; also exposes a manual refresh trigger.
 */
import { useCallback, useEffect, useState } from 'react';
import { getAnalytics } from '../services/api';
import type { StatsData } from '../types';

export interface UseAnalyticsResult {
  stats: StatsData;
  loading: boolean;
  refresh: () => void;
}

const _DEFAULT: StatsData = { total: 0, interventions: 0, complianceRate: 100 };
const POLL_MS = 30_000;

export function useAnalytics(): UseAnalyticsResult {
  const [stats, setStats]     = useState<StatsData>(_DEFAULT);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getAnalytics();
      setStats(data);
    } catch {
      // Silently retain last known value
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, POLL_MS);
    return () => clearInterval(id);
  }, [refresh]);

  return { stats, loading, refresh };
}
