"use client";

import { useCallback, useEffect, useState } from "react";

/**
 * Wraps an API promise with loading / error / retry state so pages don't
 * hang on "Loading…" forever when a fetch fails. `deps` controls refetch;
 * pass `enabled: false` to hold off (e.g. while auth context resolves).
 */
export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: React.DependencyList,
  enabled: boolean = true
): { data: T | null; error: string | null; loading: boolean; retry: () => void } {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (!enabled) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    setData(null);
    fetcher()
      .then((value) => {
        if (!cancelled) setData(value);
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Request failed");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, enabled, attempt]);

  const retry = useCallback(() => setAttempt((a) => a + 1), []);
  return { data, error, loading, retry };
}
