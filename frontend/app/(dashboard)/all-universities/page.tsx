"use client";

import { useEffect, useMemo, useState } from "react";
import { api, ProgramAlignment } from "@/lib/api";
import { MetricCard } from "@/components/MetricCard";
import { formatScore } from "@/lib/format";
import { ScoreBadge } from "@/components/ScoreBadge";

export default function AllUniversitiesPage() {
  const [rows, setRows] = useState<ProgramAlignment[] | null>(null);
  const [degreeFilter, setDegreeFilter] = useState("All");
  const [universityFilter, setUniversityFilter] = useState("All");

  useEffect(() => {
    api.allUniversities().then(setRows);
  }, []);

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

  if (!rows) return <p className="text-muted">Loading…</p>;

  return (
    <div>
      <h1 className="text-3xl font-bold text-primary-dark">🌍 All Universities</h1>
      <p className="mt-1 text-sm text-muted">National view — visible only to policy/internal accounts.</p>

      <div className="mt-6 grid grid-cols-3 gap-4">
        <MetricCard label="Universities" value={byUniversity.length} />
        <MetricCard label="Programs (scored)" value={rows.filter((r) => r.weighted_core_coverage_pct !== null).length} />
        <MetricCard label="Total programs" value={rows.length} />
      </div>

      <h2 className="mt-6 text-lg font-semibold">By university (average weighted core coverage)</h2>
      <ul className="mt-3 space-y-2">
        {byUniversity.map((u) => (
          <li key={u.university} className="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm">
            <span>
              {u.university} <span className="text-xs text-muted">({u.n} programs)</span>
            </span>
            <span className="font-semibold">{formatScore(u.avg)}</span>
          </li>
        ))}
      </ul>

      <div className="mt-8 flex items-center justify-between">
        <h2 className="text-lg font-semibold">All programs</h2>
        <div className="flex gap-3">
          <select
            value={universityFilter}
            onChange={(e) => setUniversityFilter(e.target.value)}
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
      <p className="mt-1 text-xs text-muted">Showing {filteredRows.length} of {rows.length} programs</p>

      <div className="mt-3 max-h-[560px] overflow-y-auto rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-white">
            <tr className="border-b border-border text-left text-xs text-muted">
              <th className="px-3 py-2">University</th>
              <th className="px-3 py-2">Program</th>
              <th className="px-3 py-2">Degree</th>
              <th className="px-3 py-2">Score</th>
            </tr>
          </thead>
          <tbody>
            {filteredRows.map((r) => (
              <tr key={`${r.university}-${r.program}-${r.degree}`} className="border-b border-border/60">
                <td className="px-3 py-1.5">{r.university}</td>
                <td className="px-3 py-1.5">{r.program}</td>
                <td className="px-3 py-1.5">{r.degree}</td>
                <td className="flex items-center gap-2 px-3 py-1.5">
                  {formatScore(r.weighted_core_coverage_pct)} <ScoreBadge score={r.weighted_core_coverage_pct} />
                </td>
              </tr>
            ))}
            {filteredRows.length === 0 && (
              <tr>
                <td colSpan={4} className="px-3 py-6 text-center text-muted">
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
