"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { MetricCard } from "@/components/MetricCard";
import { formatScore, scoreLabel } from "@/lib/format";
import { ErrorState, PageHeader, PageSkeleton, ScoreBar, TierLegend } from "@/components/ui";
import { useApi } from "@/lib/useApi";

export default function AllUniversitiesPage() {
  const [degreeFilter, setDegreeFilter] = useState("All");
  const [universityFilter, setUniversityFilter] = useState("All");

  const rowsQ = useApi(() => api.allUniversities(), []);
  const rows = rowsQ.data;

  const byUniversity = useMemo(() => {
    const map = new Map<string, { n: number; sum: number }>();
    for (const r of rows ?? []) {
      if (r.weighted_core_coverage_pct === null) continue;
      const e = map.get(r.university) ?? { n: 0, sum: 0 };
      e.n += 1;
      e.sum += r.weighted_core_coverage_pct;
      map.set(r.university, e);
    }
    return [...map.entries()]
      .map(([university, { n, sum }]) => ({ university, n, avg: sum / n }))
      .sort((a, b) => b.avg - a.avg);
  }, [rows]);

  const degrees = useMemo(
    () => ["All", ...Array.from(new Set((rows ?? []).map((r) => r.degree))).sort()],
    [rows]
  );
  const universities = useMemo(
    () => ["All", ...Array.from(new Set((rows ?? []).map((r) => r.university))).sort()],
    [rows]
  );

  const filteredRows = useMemo(() => {
    return (rows ?? [])
      .filter((r) => degreeFilter === "All" || r.degree === degreeFilter)
      .filter((r) => universityFilter === "All" || r.university === universityFilter)
      .slice()
      .sort((a, b) => (b.weighted_core_coverage_pct ?? -1) - (a.weighted_core_coverage_pct ?? -1));
  }, [rows, degreeFilter, universityFilter]);

  if (rowsQ.error) return <ErrorState message={rowsQ.error} onRetry={rowsQ.retry} />;
  if (!rows) return <PageSkeleton />;

  const maxAvg = Math.max(1, ...byUniversity.map((u) => u.avg));

  return (
    <div>
      <PageHeader title="All Universities" subtitle="National view — visible only to policy/internal accounts." />

      <div className="mt-6 grid grid-cols-3 gap-4">
        <MetricCard label="Universities" value={byUniversity.length} />
        <MetricCard label="Programs (scored)" value={rows.filter((r) => r.weighted_core_coverage_pct !== null).length} />
        <MetricCard label="Total programs" value={rows.length} />
      </div>

      <h2 className="mt-6 text-lg font-semibold">By university (average weighted core coverage)</h2>
      <p className="text-xs text-muted">
        Averages are portfolio means across each university&apos;s scored programs; program mixes differ, so treat
        this as an orientation, not a ranking.
      </p>
      <ul className="mt-3 space-y-2">
        {byUniversity.map((u) => (
          <li key={u.university} className="flex items-center justify-between gap-4 rounded-lg border border-border bg-surface px-3 py-2 text-sm">
            <span className="min-w-0 truncate">
              {u.university} <span className="text-xs text-muted">({u.n} programs)</span>
            </span>
            <span className="flex shrink-0 items-center gap-3">
              <span className="hidden h-1.5 w-32 overflow-hidden rounded-full bg-surface-muted sm:block" aria-hidden>
                <span className="block h-full rounded-full bg-primary/70" style={{ width: `${(u.avg / maxAvg) * 100}%` }} />
              </span>
              <span className="font-semibold tabular-nums">{formatScore(u.avg)}</span>
            </span>
          </li>
        ))}
      </ul>

      <div className="mt-8 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">All programs</h2>
        <div className="flex gap-3">
          <select
            value={universityFilter}
            onChange={(e) => setUniversityFilter(e.target.value)}
            aria-label="Filter by university"
            className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm"
          >
            {universities.map((u) => (
              <option key={u} value={u}>
                {u === "All" ? "All universities" : u}
              </option>
            ))}
          </select>
          <select
            value={degreeFilter}
            onChange={(e) => setDegreeFilter(e.target.value)}
            aria-label="Filter by degree"
            className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm"
          >
            {degrees.map((d) => (
              <option key={d} value={d}>
                {d === "All" ? "All degrees" : d}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="mt-1 flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs text-muted">Showing {filteredRows.length} of {rows.length} programs</p>
        <TierLegend />
      </div>

      <div className="mt-3 max-h-[560px] overflow-y-auto rounded-xl bg-surface shadow-card ring-1 ring-border/60">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-surface">
            <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted">
              <th className="px-3 py-2 font-medium">University</th>
              <th className="px-3 py-2 font-medium">Program</th>
              <th className="px-3 py-2 font-medium">Degree</th>
              <th className="px-3 py-2 font-medium">Alignment</th>
              <th className="px-3 py-2 font-medium">Tier</th>
            </tr>
          </thead>
          <tbody>
            {filteredRows.map((r) => (
              <tr key={`${r.university}-${r.program}-${r.degree}`} className="border-b border-border/60 last:border-0 hover:bg-surface-muted/60">
                <td className="px-3 py-1.5">{r.university}</td>
                <td className="px-3 py-1.5">
                  <Link
                    href={`/programs/${encodeURIComponent(r.program)}/${encodeURIComponent(r.degree)}?u=${encodeURIComponent(r.university)}`}
                    className="font-medium hover:text-primary hover:underline"
                  >
                    {r.program}
                  </Link>
                </td>
                <td className="px-3 py-1.5">{r.degree}</td>
                <td className="px-3 py-1.5"><ScoreBar score={r.weighted_core_coverage_pct} /></td>
                <td className="px-3 py-1.5 text-xs text-muted">{scoreLabel(r.weighted_core_coverage_pct)}</td>
              </tr>
            ))}
            {filteredRows.length === 0 && (
              <tr>
                <td colSpan={5} className="px-3 py-6 text-center text-muted">
                  No programs match this filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
