"use client";

import { AlertTriangle, Briefcase, CalendarDays, Calculator, CheckCircle2, CircleDot, FileText, GraduationCap, Settings } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/MetricCard";
import { InfoTip } from "@/components/InfoTip";
import { formatExperiment } from "@/lib/experiments";
import { formatDate, formatJobDateRange } from "@/lib/format";
import { DocBadge, ErrorState, PageHeader, PageSkeleton } from "@/components/ui";
import { useApi } from "@/lib/useApi";

function DocStatus({ score }: { score: number }) {
  if (score < 0.25)
    return <span className="inline-flex items-center gap-1 text-score-developing"><AlertTriangle className="h-3.5 w-3.5" aria-hidden /> Weak</span>;
  if (score < 0.4)
    return <span className="inline-flex items-center gap-1 text-score-moderate"><CircleDot className="h-3.5 w-3.5" aria-hidden /> Mixed</span>;
  return <span className="inline-flex items-center gap-1 text-score-strong"><CheckCircle2 className="h-3.5 w-3.5" aria-hidden /> Good</span>;
}

export default function AdminPage() {
  const { currentUniversity, universityParam, isAllUniversities } = useAuth();
  const metaQ = useApi(() => api.runMetadata(), []);
  const docQualityQ = useApi(
    () => api.docQuality(universityParam),
    [universityParam],
    !!currentUniversity && !isAllUniversities
  );
  const meta = metaQ.data;
  const docQuality = docQualityQ.data;

  if (metaQ.error) return <ErrorState message={metaQ.error} onRetry={metaQ.retry} />;
  if (!meta) return <PageSkeleton />;

  return (
    <div>
      <PageHeader
        title="Data & Admin"
        subtitle="What data this dashboard is based on, when it was collected, and when the analysis was last computed from it."
      />

      <p className="mt-4 flex items-start gap-2 rounded-lg bg-primary-50 px-4 py-3 text-sm leading-relaxed">
        <Calculator className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden />
        <span>
          <strong>Analysis generated on {formatDate(meta.created_at)}</strong> — this is when the scores you see
          throughout the dashboard were computed. It is separate from the two data-collection dates below; the
          underlying data can be older than the analysis date if nothing has changed since collection.
        </span>
      </p>

      <h2 className="mt-6 inline-flex items-center gap-2 text-lg font-semibold">
        <CalendarDays className="h-4 w-4 text-primary" aria-hidden /> What data was used, and when it was collected
      </h2>
      <p className="text-xs leading-relaxed text-muted">
        Two independent datasets feed every score: the courses each university publishes, and job postings from
        the Armenian IT market. Both are one-time snapshots, refreshed manually.
      </p>
      <div className="mt-2 grid grid-cols-2 gap-6 text-sm">
        <Card>
          <div className="inline-flex items-center gap-2 font-semibold">
            <Briefcase className="h-4 w-4 text-primary" aria-hidden /> Job market data
          </div>
          <p className="mt-1 leading-relaxed text-muted">
            Status: Static snapshot (not live)
            <br />
            Postings collected:{" "}
            <strong>{formatJobDateRange(meta.job_snapshot.earliest_at, meta.job_snapshot.collected_at)}</strong>
            {(meta.job_snapshot.n_unknown_date ?? 0) > 0 && (
              <> ({meta.job_snapshot.n_unknown_date} active postings have no known collection date)</>
            )}
            <br />
            IT postings analyzed: <strong>{meta.job_snapshot.n_it_postings?.toLocaleString()}</strong>
            <br />
            From sources: <strong>{meta.job_snapshot.n_sources}</strong> Armenian job boards / company career
            pages
          </p>
        </Card>
        <Card>
          <div className="inline-flex items-center gap-2 font-semibold">
            <GraduationCap className="h-4 w-4 text-primary" aria-hidden /> Curriculum data
          </div>
          <p className="mt-1 leading-relaxed text-muted">
            Status: Static snapshot (not live)
            <br />
            Course catalog data collected on: <strong>{formatDate(meta.curriculum_snapshot.collected_at)}</strong>
            <br />
            Courses analyzed: <strong>{meta.curriculum_snapshot.n_courses?.toLocaleString()}</strong>
            <br />
            Across <strong>{meta.curriculum_snapshot.n_programs}</strong> programs at{" "}
            <strong>{meta.curriculum_snapshot.n_universities}</strong> universities
          </p>
        </Card>
      </div>

      <h2 className="mt-6 inline-flex items-center gap-2 text-lg font-semibold">
        <Settings className="h-4 w-4 text-primary" aria-hidden /> How the analysis was computed
      </h2>
      <Card className="mt-2 text-sm">
        <p className="leading-relaxed">
          <strong>Method used:</strong> {formatExperiment(meta.experiment)} <InfoTip term="experiment" />
          <br />
          <strong>Run identifier:</strong> <span className="font-mono text-xs">{meta.run_id}</span> (for citing
          this exact analysis run)
          <br />
          <strong>Notes:</strong> {meta.notes ?? "—"}
        </p>
      </Card>

      {isAllUniversities && (
        <p className="mt-6 rounded-lg bg-surface px-4 py-3 text-sm text-muted shadow-card ring-1 ring-border/60">
          Documentation quality is reported per university — select a specific university in the switcher above to
          see it.
        </p>
      )}

      {docQualityQ.error && <ErrorState message={docQualityQ.error} onRetry={docQualityQ.retry} />}

      {docQuality && (
        <>
          <h2 className="mt-6 inline-flex items-center gap-2 text-lg font-semibold">
            <FileText className="h-4 w-4 text-primary" aria-hidden /> Documentation quality by program{" "}
            <InfoTip term="doc_score" />
          </h2>
          <p className="max-w-3xl text-xs leading-relaxed text-muted">
            Programs with low documentation quality may show lower alignment scores because there wasn&apos;t much
            published course detail to analyze — not necessarily because the curriculum itself is weak. &ldquo;Data
            level&rdquo; below shows exactly what was published per program: how many courses have no description at
            all, how many were filled in with an AI-generated description because none existed, how many have only a
            short/thin one, and how many have a full published description. See{" "}
            <a href="/methodology#fairness" className="font-medium text-primary">Methodology</a> for more.
          </p>
          <div className="mt-3 overflow-x-auto rounded-xl bg-surface shadow-card ring-1 ring-border/60">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted">
                  <th className="px-3 py-2 font-medium">Program</th>
                  <th className="px-3 py-2 font-medium">Degree</th>
                  <th className="px-3 py-2 font-medium">Courses</th>
                  <th className="px-3 py-2 font-medium">Documentation level</th>
                  <th className="px-3 py-2 font-medium">Doc. quality</th>
                  <th className="px-3 py-2 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {docQuality.programs.map((p) => (
                  <tr key={`${p.program}-${p.degree}`} className="border-b border-border/60 last:border-0">
                    <td className="px-3 py-1.5">{p.program}</td>
                    <td className="px-3 py-1.5">{p.degree}</td>
                    <td className="px-3 py-1.5 tabular-nums">{p.n_courses}</td>
                    <td className="px-3 py-1.5">
                      <DocBadge level={p.documentation_level} showFull />
                      <div className="text-[10px] text-muted">
                        {p.n_missing > 0 && <>{p.n_missing} no description</>}
                        {p.n_missing > 0 && (p.n_ai_generated > 0 || p.n_short > 0) && " · "}
                        {p.n_ai_generated > 0 && <>{p.n_ai_generated} AI-generated</>}
                        {p.n_ai_generated > 0 && p.n_short > 0 && " · "}
                        {p.n_short > 0 && <>{p.n_short} very short</>}
                      </div>
                    </td>
                    <td className="px-3 py-1.5 tabular-nums">{(p.doc_score * 100).toFixed(0)}%</td>
                    <td className="px-3 py-1.5 text-xs"><DocStatus score={p.doc_score} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-muted">
            Doc. quality/Status is the skill-extraction confidence score described above: Good (≥40%) · Mixed
            (25–40%) · Weak (&lt;25%)
          </p>

          {docQuality.missing_descriptions.length > 0 && (
            <>
              <h2 className="mt-6 inline-flex items-center gap-2 text-lg font-semibold">
                <AlertTriangle className="h-4 w-4 text-score-moderate" aria-hidden /> Courses with missing or short
                descriptions
              </h2>
              <p className="text-xs text-muted">
                {docQuality.missing_descriptions.length} courses cannot be analyzed for skill alignment.
              </p>
              <ul className="mt-3 space-y-1">
                {docQuality.missing_descriptions.slice(0, 30).map((c, i) => (
                  <li key={i} className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm">
                    {c.course_name} <span className="text-xs text-muted">({c.program_name}, {c.degree_level})</span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </>
      )}
    </div>
  );
}
