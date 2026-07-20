"use client";

import { useEffect, useState } from "react";
import { CalendarDays, Eye } from "lucide-react";
import { api, RunMetadata } from "@/lib/api";
import { ALL_UNIVERSITIES, useAuth } from "@/lib/auth-context";
import { formatDate } from "@/lib/format";

/**
 * Slim persistent bar above page content: data-freshness chip on every page
 * (a reproducibility requirement — snapshot visibility shouldn't depend on
 * scrolling to a footer note) and, for admins, the university switcher.
 */
export function TopBar() {
  const { canSwitchUniversity, currentUniversity, switchUniversity, user } = useAuth();
  const [universities, setUniversities] = useState<string[]>([]);
  const [meta, setMeta] = useState<RunMetadata | null>(null);

  useEffect(() => {
    if (canSwitchUniversity) {
      api.universities().then(setUniversities).catch(() => {});
    }
  }, [canSwitchUniversity]);

  useEffect(() => {
    api.runMetadata().then(setMeta).catch(() => {});
  }, []);

  return (
    <div className="mb-6 flex flex-wrap items-center justify-between gap-3 border-b border-border pb-3">
      <div className="flex items-center gap-2 text-xs text-muted">
        <CalendarDays className="h-3.5 w-3.5" aria-hidden />
        {meta ? (
          <span>
            Job market snapshot: <strong className="font-medium text-foreground">{formatDate(meta.job_snapshot.collected_at)}</strong>
            {meta.job_snapshot.n_it_postings != null && <> · {meta.job_snapshot.n_it_postings} IT postings</>}
          </span>
        ) : (
          <span>Loading snapshot info…</span>
        )}
      </div>

      {canSwitchUniversity && (
        <div className="flex items-center gap-3">
          <select
            value={currentUniversity ?? ""}
            onChange={(e) => switchUniversity(e.target.value)}
            aria-label="Switch university"
            className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm font-medium"
          >
            <option value={ALL_UNIVERSITIES}>All universities</option>
            {universities.map((u) => (
              <option key={u} value={u}>
                {u}
              </option>
            ))}
          </select>
          <span className="inline-flex items-center gap-1 whitespace-nowrap text-xs text-muted">
            <Eye className="h-3.5 w-3.5" aria-hidden /> {user?.role}
          </span>
        </div>
      )}
    </div>
  );
}
