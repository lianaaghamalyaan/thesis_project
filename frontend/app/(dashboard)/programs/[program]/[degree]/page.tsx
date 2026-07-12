"use client";

import { use, useEffect, useState } from "react";
import { api, ProgramDetail } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ScoreDisplay } from "@/components/ScoreBadge";
import { MetricCard, Card } from "@/components/MetricCard";
import { formatScore, GAP_TYPE_ICONS, GAP_TYPE_LABELS } from "@/lib/format";

export default function ProgramDetailPage({
  params,
}: {
  params: Promise<{ program: string; degree: string }>;
}) {
  const { program: rawProgram, degree: rawDegree } = use(params);
  const program = decodeURIComponent(rawProgram);
  const degree = decodeURIComponent(rawDegree);
  const { currentUniversity } = useAuth();
  const [detail, setDetail] = useState<ProgramDetail | null>(null);
  const [tab, setTab] = useState<"strengths" | "gaps">("strengths");

  useEffect(() => {
    if (!currentUniversity) return;
    setDetail(null);
    api.programDetail(program, degree, currentUniversity).then(setDetail);
  }, [program, degree, currentUniversity]);

  if (!detail) return <p className="text-muted">Loading…</p>;

  const { alignment, gaps, fallback_gaps, strengths, benchmark, doc_score, gap_type } = detail;
  const score = alignment?.core_role_coverage_pct ?? null;
  const displayGaps = gaps.length
    ? gaps.map((g) => ({ skill: g.missing_skill, freq: g.job_frequency, category: g.category }))
    : fallback_gaps.map((g) => ({ skill: g.gap_skill, freq: g.job_frequency, category: null }));

  return (
    <div>
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-primary-dark">{program}</h1>
          <p className="mt-1 text-sm text-muted">
            {degree} · {currentUniversity}
          </p>
        </div>
        <a
          href={currentUniversity ? api.programBriefPdfUrl(program, degree, currentUniversity) : "#"}
          className="rounded-lg border border-border px-3 py-1.5 text-sm font-medium hover:bg-surface"
        >
          📄 Export program brief (PDF)
        </a>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-[220px_1fr]">
        <div className="flex flex-col items-center justify-center rounded-xl border border-border bg-surface py-6">
          <ScoreDisplay score={score} />
          <div className="mt-1 text-xs text-muted">Core role-aware coverage</div>
        </div>
        <div className="text-sm">
          <p>
            This program covers approximately <strong>{score !== null ? Math.round(score) : "—"}%</strong> of the
            skills commonly required in <strong>{alignment?.relevant_roles ?? "general IT"}</strong> job postings in
            the Armenian IT market.
          </p>
          <p className="mt-2 text-muted">
            Covers {alignment?.core_n_overlap ?? "—"} of {alignment?.core_n_job_skills ?? "—"} core skills ·{" "}
            {displayGaps.length} skills identified as gaps
          </p>
          <p className="mt-2 text-xs text-muted">📌 Relevant roles: {alignment?.relevant_roles ?? "unmapped"}</p>
        </div>
      </div>

      {benchmark && score !== null && (
        <>
          <h2 className="mt-8 text-base font-semibold">📊 How this compares</h2>
          <div className="mt-3 grid grid-cols-3 gap-4">
            <MetricCard label="This program" value={formatScore(score)} />
            <MetricCard label={`Peer average (n=${benchmark.peer_n})`} value={formatScore(benchmark.peer_mean)} />
            <MetricCard
              label="Difference"
              value={`${score - benchmark.peer_mean >= 0 ? "+" : ""}${(score - benchmark.peer_mean).toFixed(1)} pts`}
            />
          </div>
          <p className="mt-2 text-xs text-muted">
            Compared against {benchmark.peer_n} programs at other Armenian universities, matched by{" "}
            {benchmark.matched_on}. Peer best observed: {formatScore(benchmark.peer_max)}.
          </p>
        </>
      )}

      <hr className="my-6 border-border" />

      <div className="flex gap-1 border-b border-border">
        {(["strengths", "gaps"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium ${
              tab === t ? "border-b-2 border-primary text-primary" : "text-muted"
            }`}
          >
            {t === "strengths" ? "✅ Strengths" : "⚠️ Gaps"}
          </button>
        ))}
      </div>

      {tab === "strengths" && (
        <ul className="mt-4 space-y-2">
          {strengths.length === 0 && <p className="text-sm text-muted">No mapped role data for this program.</p>}
          {strengths.map((s) => (
            <li key={s.skill} className="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm">
              <span>{s.skill}</span>
              <span className="text-xs text-muted">{s.job_count} job postings</span>
            </li>
          ))}
        </ul>
      )}

      {tab === "gaps" && (
        <div className="mt-4">
          {doc_score <= 0.2 && (
            <Card className="mb-4 border-score-moderate bg-orange-50">
              <p className="text-sm">
                ⚠️ <strong>Documentation quality notice:</strong> course descriptions for this program are limited.
                Some gaps below may be documentation gaps — the skills could already be taught but are not
                explicitly mentioned in course syllabi.
              </p>
            </Card>
          )}
          <ul className="space-y-2">
            {displayGaps.map((g, i) => (
              <li key={i} className="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm">
                <span>
                  {GAP_TYPE_ICONS[gap_type]} {g.skill}
                </span>
                <span className="text-xs text-muted">
                  {g.freq ?? 0} job postings · {GAP_TYPE_LABELS[gap_type]}
                </span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-xs text-muted">
            Documentation quality score for this program: {(doc_score * 100).toFixed(0)}% (proportion of extracted
            skills with high extraction confidence)
          </p>
        </div>
      )}
    </div>
  );
}
