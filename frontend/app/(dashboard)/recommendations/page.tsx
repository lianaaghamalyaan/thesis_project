"use client";

import { useEffect, useState } from "react";
import { api, RecommendationsResponse } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/MetricCard";
import { formatScore } from "@/lib/format";

const PRIORITY_COLORS: Record<string, string> = {
  high: "var(--score-developing)",
  medium: "var(--score-moderate)",
  info: "var(--primary)",
};

export default function RecommendationsPage() {
  const { currentUniversity, universityParam, isAllUniversities } = useAuth();
  const [data, setData] = useState<RecommendationsResponse | null>(null);

  useEffect(() => {
    if (!currentUniversity || isAllUniversities) return;
    setData(null);
    api.recommendations(universityParam).then(setData);
  }, [currentUniversity, universityParam, isAllUniversities]);

  if (isAllUniversities) {
    return (
      <div>
        <h1 className="text-3xl font-bold text-primary-dark">Recommendations</h1>
        <p className="mt-4 rounded-lg bg-surface px-4 py-3 text-sm text-muted">
          Recommendations are generated per university — select a specific university in the banner above to see
          them. (Program names can repeat across universities, which would make cross-university aggregation here
          ambiguous.)
        </p>
      </div>
    );
  }

  if (!data) return <p className="text-muted">Loading…</p>;

  const docGaps = data.programs.filter((p) => p.gap_type === "documentation_gap");
  const curriculumGaps = data.programs.filter((p) => p.gap_type === "curriculum_gap");

  return (
    <div>
      <h1 className="text-3xl font-bold text-primary-dark">Recommendations</h1>
      <p className="mt-1 text-sm text-muted">Priority matrix and data-driven suggestions per program.</p>

      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
        <div>
          <h2 className="text-base font-semibold text-score-moderate">🟡 Likely documentation gaps</h2>
          <p className="text-xs text-muted">Improving syllabi could raise scores without curriculum changes.</p>
          <ul className="mt-3 space-y-2">
            {docGaps.map((p) => (
              <li key={`${p.program}-${p.degree}`} className="rounded-lg border border-border px-3 py-2 text-sm">
                {p.program} ({p.degree}) — {formatScore(p.core_role_coverage_pct)}
              </li>
            ))}
            {docGaps.length === 0 && <p className="text-sm text-muted">None flagged.</p>}
          </ul>
        </div>
        <div>
          <h2 className="text-base font-semibold text-score-developing">🔴 Likely curriculum gaps</h2>
          <p className="text-xs text-muted">Well-documented programs where skills are genuinely missing.</p>
          <ul className="mt-3 space-y-2">
            {curriculumGaps.map((p) => (
              <li key={`${p.program}-${p.degree}`} className="rounded-lg border border-border px-3 py-2 text-sm">
                {p.program} ({p.degree}) — {formatScore(p.core_role_coverage_pct)}
              </li>
            ))}
            {curriculumGaps.length === 0 && <p className="text-sm text-muted">None flagged.</p>}
          </ul>
        </div>
      </div>

      <h2 className="mt-8 text-lg font-semibold">University-wide gap priorities</h2>
      <p className="text-xs text-muted">Skills missing across the most programs — highest-leverage additions.</p>
      <ul className="mt-3 space-y-1">
        {data.cross_program_gaps.slice(0, 10).map((g) => (
          <li key={g.gap_skill} className="flex items-center justify-between rounded-lg border border-border px-3 py-1.5 text-sm">
            <span>{g.gap_skill}</span>
            <span className="text-xs text-muted">
              {g.n_programs} programs · {g.total_frequency} postings
            </span>
          </li>
        ))}
      </ul>

      <h2 className="mt-8 text-lg font-semibold">Per-program recommendations</h2>
      <div className="mt-3 space-y-4">
        {data.programs.map((p) => (
          <Card key={`${p.program}-${p.degree}`}>
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">
                {p.program} <span className="font-normal text-muted">({p.degree})</span>
              </h3>
              <span className="text-sm font-semibold">{formatScore(p.core_role_coverage_pct)}</span>
            </div>
            <ul className="mt-3 space-y-2">
              {p.recommendations.map((r, i) => (
                <li key={i} className="border-l-2 pl-3 text-sm" style={{ borderColor: PRIORITY_COLORS[r.priority] ?? "var(--border)" }}>
                  <div className="font-medium">{r.title}</div>
                  <div className="text-muted">{r.description}</div>
                </li>
              ))}
            </ul>
          </Card>
        ))}
      </div>
    </div>
  );
}
