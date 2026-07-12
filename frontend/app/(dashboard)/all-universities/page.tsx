"use client";

import { useEffect, useMemo, useState } from "react";
import { api, ProgramAlignment } from "@/lib/api";
import { MetricCard } from "@/components/MetricCard";
import { formatScore } from "@/lib/format";
import { ScoreBadge } from "@/components/ScoreBadge";

export default function AllUniversitiesPage() {
  const [rows, setRows] = useState<ProgramAlignment[] | null>(null);

  useEffect(() => {
    api.allUniversities().then(setRows);
  }, []);

  const byUniversity = useMemo(() => {
    const map = new Map<string, { n: number; sum: number }>();
    for (const r of rows ?? []) {
      if (r.core_role_coverage_pct === null) continue;
      const e = map.get(r.university) ?? { n: 0, sum: 0 };
      e.n += 1;
      e.sum += r.core_role_coverage_pct;
      map.set(r.university, e);
    }
    return [...map.entries()]
      .map(([university, { n, sum }]) => ({ university, n, avg: sum / n }))
      .sort((a, b) => b.avg - a.avg);
  }, [rows]);

  if (!rows) return <p className="text-muted">Loading…</p>;

  return (
    <div>
      <h1 className="text-3xl font-bold text-primary-dark">🌍 All Universities</h1>
      <p className="mt-1 text-sm text-muted">National view — visible only to policy/internal accounts.</p>

      <div className="mt-6 grid grid-cols-3 gap-4">
        <MetricCard label="Universities" value={byUniversity.length} />
        <MetricCard label="Programs (scored)" value={rows.filter((r) => r.core_role_coverage_pct !== null).length} />
        <MetricCard label="Total programs" value={rows.length} />
      </div>

      <h2 className="mt-6 text-lg font-semibold">By university (average core coverage)</h2>
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

      <h2 className="mt-6 text-lg font-semibold">All programs</h2>
      <table className="mt-3 w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-xs text-muted">
            <th className="py-2">University</th>
            <th>Program</th>
            <th>Degree</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {rows
            .slice()
            .sort((a, b) => (b.core_role_coverage_pct ?? -1) - (a.core_role_coverage_pct ?? -1))
            .map((r) => (
              <tr key={`${r.university}-${r.program}-${r.degree}`} className="border-b border-border/60">
                <td className="py-1.5">{r.university}</td>
                <td>{r.program}</td>
                <td>{r.degree}</td>
                <td className="flex items-center gap-2 py-1.5">
                  {formatScore(r.core_role_coverage_pct)} <ScoreBadge score={r.core_role_coverage_pct} />
                </td>
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  );
}
