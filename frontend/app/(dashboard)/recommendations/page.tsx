"use client";

import Link from "next/link";
import { AlertCircle, FileText, Wrench } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/MetricCard";
import { DataFreshnessNote } from "@/components/DataFreshnessNote";
import { ErrorState, PageHeader, PageSkeleton, ScoreBar } from "@/components/ui";
import { formatScore } from "@/lib/format";
import { useApi } from "@/lib/useApi";

const PRIORITY_COLORS: Record<string, string> = {
  high: "var(--score-developing)",
  medium: "var(--score-moderate)",
  info: "var(--primary)",
};

const PRIORITY_LABELS: Record<string, string> = {
  high: "High priority",
  medium: "Medium priority",
  info: "Note",
};

export default function RecommendationsPage() {
  const { currentUniversity, universityParam, isAllUniversities } = useAuth();
  const metaQ = useApi(() => api.runMetadata(), []);
  const dataQ = useApi(
    () => api.recommendations(universityParam),
    [universityParam],
    !!currentUniversity && !isAllUniversities
  );
  const data = dataQ.data;

  if (isAllUniversities) {
    return (
      <div>
        <PageHeader
          title="Recommendations"
          subtitle="Recommendations are generated per university — select a specific university in the switcher above to see them. (Program names can repeat across universities, which would make cross-university aggregation here ambiguous.)"
        />
      </div>
    );
  }

  if (dataQ.error) return <ErrorState message={dataQ.error} onRetry={dataQ.retry} />;
  if (!data) return <PageSkeleton />;

  const docGaps = data.programs.filter((p) => p.gap_type === "documentation_gap");
  const curriculumGaps = data.programs.filter((p) => p.gap_type === "curriculum_gap");
  const maxCrossGapPrograms = Math.max(1, ...data.cross_program_gaps.map((g) => g.n_programs));

  return (
    <div>
      <PageHeader
        title="Recommendations"
        subtitle="What to do next, per program — separated into documentation fixes (update course descriptions) and curriculum changes (add or revise course content), because they need different owners and effort."
      />

      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
        <Card>
          <h2 className="inline-flex items-center gap-2 text-base font-semibold text-score-moderate">
            <FileText className="h-4 w-4" aria-hidden /> Likely documentation gaps
          </h2>
          <p className="mt-1 text-xs leading-relaxed text-muted">
            These programs&apos; published course descriptions are thin, so their scores are probably understated.
            <strong> Action: publish or expand course descriptions</strong> — scores could rise without any curriculum
            change.
          </p>
          <ul className="mt-3 space-y-2">
            {docGaps.map((p) => (
              <li key={`${p.program}-${p.degree}`} className="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm">
                <span>{p.program} <span className="text-muted">({p.degree})</span></span>
                <ScoreBar score={p.weighted_core_coverage_pct} width="w-20" />
              </li>
            ))}
            {docGaps.length === 0 && <p className="text-sm text-muted">None flagged.</p>}
          </ul>
        </Card>
        <Card>
          <h2 className="inline-flex items-center gap-2 text-base font-semibold text-score-developing">
            <Wrench className="h-4 w-4" aria-hidden /> Likely curriculum gaps
          </h2>
          <p className="mt-1 text-xs leading-relaxed text-muted">
            These programs are well documented, so their gaps are more likely real.{" "}
            <strong>Action: review course content</strong> against the gap skills on each program&apos;s detail page.
          </p>
          <ul className="mt-3 space-y-2">
            {curriculumGaps.map((p) => (
              <li key={`${p.program}-${p.degree}`} className="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm">
                <span>{p.program} <span className="text-muted">({p.degree})</span></span>
                <ScoreBar score={p.weighted_core_coverage_pct} width="w-20" />
              </li>
            ))}
            {curriculumGaps.length === 0 && <p className="text-sm text-muted">None flagged.</p>}
          </ul>
        </Card>
      </div>

      <h2 className="mt-8 text-lg font-semibold">University-wide gap priorities</h2>
      <p className="text-xs text-muted">
        Skills missing across the most programs — the highest-leverage additions for the university as a whole.
      </p>
      <ul className="mt-3 space-y-1">
        {data.cross_program_gaps.slice(0, 10).map((g) => (
          <li key={g.gap_skill} className="flex items-center justify-between gap-4 rounded-lg border border-border bg-surface px-3 py-1.5 text-sm">
            <span className="min-w-0 truncate">{g.gap_skill}</span>
            <span className="flex shrink-0 items-center gap-3 text-xs text-muted">
              <span className="hidden h-1.5 w-24 overflow-hidden rounded-full bg-surface-muted sm:block" aria-hidden>
                <span
                  className="block h-full rounded-full bg-primary/70"
                  style={{ width: `${(g.n_programs / maxCrossGapPrograms) * 100}%` }}
                />
              </span>
              missing in {g.n_programs} programs · {g.total_frequency} postings
            </span>
          </li>
        ))}
      </ul>

      <h2 className="mt-8 text-lg font-semibold">Per-program recommendations</h2>
      <div className="mt-3 space-y-4">
        {data.programs.map((p) => (
          <Card key={`${p.program}-${p.degree}`}>
            <div className="flex items-center justify-between gap-4">
              <h3 className="font-semibold">
                <Link
                  href={`/programs/${encodeURIComponent(p.program)}/${encodeURIComponent(p.degree)}?u=${encodeURIComponent(currentUniversity ?? "")}`}
                  className="hover:text-primary hover:underline"
                >
                  {p.program} <span className="font-normal text-muted">({p.degree})</span>
                </Link>
              </h3>
              <span className="text-sm font-semibold">{formatScore(p.weighted_core_coverage_pct)}</span>
            </div>
            <ul className="mt-3 space-y-2.5">
              {p.recommendations.map((r, i) => (
                <li key={i} className="border-l-2 pl-3 text-sm" style={{ borderColor: PRIORITY_COLORS[r.priority] ?? "var(--border)" }}>
                  <div className="flex items-center gap-2 font-medium">
                    {r.priority === "high" && <AlertCircle className="h-3.5 w-3.5 text-score-developing" aria-hidden />}
                    {r.title}
                    <span className="rounded-full bg-surface-muted px-2 py-0.5 text-[10px] font-medium text-muted">
                      {PRIORITY_LABELS[r.priority] ?? r.priority}
                    </span>
                  </div>
                  <div className="mt-0.5 leading-relaxed text-muted">{r.description}</div>
                </li>
              ))}
            </ul>
          </Card>
        ))}
      </div>

      <DataFreshnessNote meta={metaQ.data} />
    </div>
  );
}
