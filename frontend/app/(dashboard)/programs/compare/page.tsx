"use client";

import { Suspense, useMemo } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { api, ProgramDetail } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ScoreGauge } from "@/components/ScoreGauge";
import { InfoTip } from "@/components/InfoTip";
import { ErrorState, PageHeader, PageSkeleton, TierLegend } from "@/components/ui";
import { formatScore } from "@/lib/format";
import { useApi } from "@/lib/useApi";

// URL shape: /programs/compare?a=program|degree|university&b=program|degree|university
type Target = { program: string; degree: string; university: string };

function parseTarget(raw: string | null): Target | null {
  if (!raw) return null;
  const [program, degree, university] = raw.split("|");
  if (!program || !degree || !university) return null;
  return { program, degree, university };
}

function gapSkills(detail: ProgramDetail): Set<string> {
  return new Set(
    detail.gaps.length ? detail.gaps.map((g) => g.missing_skill) : detail.fallback_gaps.map((g) => g.gap_skill)
  );
}

function ComparePageInner() {
  const { currentUniversity } = useAuth();
  const searchParams = useSearchParams();
  const a = parseTarget(searchParams.get("a"));
  const b = parseTarget(searchParams.get("b"));

  const aQ = useApi(
    () => api.programDetail(a!.program, a!.degree, a!.university),
    [searchParams.get("a")],
    !!currentUniversity && !!a
  );
  const bQ = useApi(
    () => api.programDetail(b!.program, b!.degree, b!.university),
    [searchParams.get("b")],
    !!currentUniversity && !!b
  );

  const shared = useMemo(() => {
    if (!aQ.data || !bQ.data) return { both: [] as string[], onlyA: [] as string[], onlyB: [] as string[] };
    const ga = gapSkills(aQ.data);
    const gb = gapSkills(bQ.data);
    return {
      both: [...ga].filter((s) => gb.has(s)).sort(),
      onlyA: [...ga].filter((s) => !gb.has(s)).sort(),
      onlyB: [...gb].filter((s) => !ga.has(s)).sort(),
    };
  }, [aQ.data, bQ.data]);

  if (!a || !b) {
    return (
      <div>
        <PageHeader title="Compare programs" subtitle="Select two programs on the Programs page to compare them side by side." />
        <Link href="/programs" className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-primary hover:underline">
          <ArrowLeft className="h-4 w-4" aria-hidden /> Back to Programs
        </Link>
      </div>
    );
  }

  if (aQ.error) return <ErrorState message={aQ.error} onRetry={aQ.retry} />;
  if (bQ.error) return <ErrorState message={bQ.error} onRetry={bQ.retry} />;
  if (!aQ.data || !bQ.data) return <PageSkeleton />;

  const cols: { target: Target; detail: ProgramDetail }[] = [
    { target: a, detail: aQ.data },
    { target: b, detail: bQ.data },
  ];

  return (
    <div>
      <PageHeader title="Compare programs" subtitle="Side-by-side view of two programs — scores, coverage, and where their gaps overlap or differ." />
      <Link href="/programs" className="mt-2 inline-flex items-center gap-1.5 text-sm font-medium text-primary hover:underline">
        <ArrowLeft className="h-4 w-4" aria-hidden /> Back to Programs
      </Link>

      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
        {cols.map(({ target, detail }) => {
          const alignment = detail.alignment;
          const score = alignment?.weighted_core_coverage_pct ?? null;
          const nGaps = detail.gaps.length || detail.fallback_gaps.length;
          return (
            <div key={`${target.program}|${target.degree}|${target.university}`} className="rounded-xl bg-surface p-5 shadow-card ring-1 ring-border/60">
              <h2 className="font-display text-xl font-bold text-primary-dark">
                <Link
                  href={`/programs/${encodeURIComponent(target.program)}/${encodeURIComponent(target.degree)}?u=${encodeURIComponent(target.university)}`}
                  className="hover:underline"
                >
                  {target.program}
                </Link>
              </h2>
              <p className="text-sm text-muted">
                {target.degree} · {target.university}
              </p>
              <div className="mt-4 flex justify-center">
                <ScoreGauge score={score} />
              </div>
              <dl className="mt-4 space-y-1.5 text-sm">
                <div className="flex justify-between gap-4">
                  <dt className="text-muted">Relevant roles</dt>
                  <dd className="text-right">{alignment?.relevant_roles ?? "general IT"}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-muted">Core skills covered</dt>
                  <dd className="tabular-nums">
                    {alignment?.core_n_overlap ?? "—"} of {alignment?.core_n_job_skills ?? "—"}
                  </dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-muted">Gap skills</dt>
                  <dd className="tabular-nums">{nGaps}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-muted">
                    Documentation quality <InfoTip term="doc_score" />
                  </dt>
                  <dd className="tabular-nums">{(detail.doc_score * 100).toFixed(0)}%</dd>
                </div>
                {detail.benchmark && (
                  <div className="flex justify-between gap-4">
                    <dt className="text-muted">Peer average</dt>
                    <dd className="tabular-nums">{formatScore(detail.benchmark.peer_mean)}</dd>
                  </div>
                )}
              </dl>
            </div>
          );
        })}
      </div>

      <TierLegend className="mt-3" />

      <h2 className="mt-8 text-lg font-semibold">Gap overlap</h2>
      <p className="max-w-3xl text-xs leading-relaxed text-muted">
        Skills the market demands that each program is missing. Shared gaps are candidates for a university-level
        response; gaps unique to one program show where the other already covers the skill. Note: if the two
        programs target different role groups, their gap lists are measured against different job markets.
      </p>
      <div className="mt-3 grid grid-cols-1 gap-6 md:grid-cols-3">
        <div>
          <h3 className="text-sm font-semibold">Both missing ({shared.both.length})</h3>
          <ul className="mt-2 space-y-1">
            {shared.both.map((s) => (
              <li key={s} className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm">{s}</li>
            ))}
            {shared.both.length === 0 && <p className="text-sm text-muted">No shared gaps.</p>}
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold">
            Only {a.program} ({a.degree}) missing ({shared.onlyA.length})
          </h3>
          <ul className="mt-2 space-y-1">
            {shared.onlyA.map((s) => (
              <li key={s} className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm">{s}</li>
            ))}
            {shared.onlyA.length === 0 && <p className="text-sm text-muted">None.</p>}
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold">
            Only {b.program} ({b.degree}) missing ({shared.onlyB.length})
          </h3>
          <ul className="mt-2 space-y-1">
            {shared.onlyB.map((s) => (
              <li key={s} className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm">{s}</li>
            ))}
            {shared.onlyB.length === 0 && <p className="text-sm text-muted">None.</p>}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <ComparePageInner />
    </Suspense>
  );
}
