"use client";

import { use, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api, ProgramDetail, RunMetadata, SkillInfo } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ScoreDisplay } from "@/components/ScoreBadge";
import { MetricCard, Card } from "@/components/MetricCard";
import { InfoTip, TextTip } from "@/components/InfoTip";
import { DataFreshnessNote } from "@/components/DataFreshnessNote";
import { formatScore, GAP_TYPE_ICONS, GAP_TYPE_LABELS } from "@/lib/format";

const LOW_DOC_THRESHOLD = 0.25;

export default function ProgramDetailPage({
  params,
}: {
  params: Promise<{ program: string; degree: string }>;
}) {
  const { program: rawProgram, degree: rawDegree } = use(params);
  const program = decodeURIComponent(rawProgram);
  const degree = decodeURIComponent(rawDegree);
  const { currentUniversity, universityParam } = useAuth();
  // A `?u=` query param pins the university explicitly — required in the
  // admin "All universities" mode, where the same program name + degree can
  // exist at two universities (e.g. "Informatics (Computer Science)" at
  // both NPUA and NUACA) and the session's current university is no help.
  const searchParams = useSearchParams();
  const pinnedUniversity = searchParams.get("u");
  const [loadedDetail, setLoadedDetail] = useState<{ key: string; value: ProgramDetail } | null>(null);
  const [meta, setMeta] = useState<RunMetadata | null>(null);
  const [tab, setTab] = useState<"strengths" | "gaps" | "evidence">("strengths");
  const [skillInfo, setSkillInfo] = useState<Record<string, SkillInfo>>({});

  useEffect(() => {
    api.runMetadata().then(setMeta);
  }, []);

  const effectiveUniversity = pinnedUniversity ?? universityParam ?? null;
  const detailKey = `${program}\u0000${degree}\u0000${effectiveUniversity ?? ""}`;
  const detail = loadedDetail?.key === detailKey ? loadedDetail.value : null;

  // Batch-fetch "what is this skill?" context for every skill shown on this
  // page in one request, instead of one per skill.
  const allSkillNames = useMemo(() => {
    if (!detail) return [];
    const gapNames = detail.gaps.length
      ? detail.gaps.map((g) => g.missing_skill)
      : detail.fallback_gaps.map((g) => g.gap_skill);
    return Array.from(new Set([...detail.strengths.map((s) => s.skill), ...gapNames]));
  }, [detail]);

  useEffect(() => {
    if (allSkillNames.length === 0) return;
    api.skillsInfo(allSkillNames).then(setSkillInfo);
  }, [allSkillNames]);

  useEffect(() => {
    if (!currentUniversity) return;
    if (!effectiveUniversity) return; // ALL mode with no ?u= — wait for pin
    api.programDetail(program, degree, effectiveUniversity).then((value) => {
      setLoadedDetail({ key: detailKey, value });
    });
  }, [program, degree, currentUniversity, effectiveUniversity, detailKey]);

  if (!detail) return <p className="text-muted">Loading…</p>;

  const { alignment, gaps, fallback_gaps, strengths, skill_courses, benchmark, doc_score, gap_type, course_evidence, program_outcomes } = detail;
  // weighted_core_coverage_pct is the headline metric (frequency-weighted,
  // so high-demand skills dominate — see pipeline/compute_alignment.py's
  // docstring for why this replaced the unweighted core_role_coverage_pct).
  const score = alignment?.weighted_core_coverage_pct ?? null;
  const displayGaps = gaps.length
    ? gaps.map((g) => ({ skill: g.missing_skill, freq: g.job_frequency, pct: g.pct_of_role_postings, category: g.category }))
    : fallback_gaps.map((g) => ({ skill: g.gap_skill, freq: g.job_frequency, pct: g.pct_of_role_postings, category: null }));

  return (
    <div>
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-primary-dark">{program}</h1>
          <p className="mt-1 text-sm text-muted">
            {degree} · {effectiveUniversity}
          </p>
          {alignment?.source_url && (
            <a
              href={alignment.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-1 inline-block text-sm font-medium text-primary hover:underline"
            >
              🔗 View official curriculum on university website →
            </a>
          )}
        </div>
        <a
          href={effectiveUniversity ? api.programBriefPdfUrl(program, degree, effectiveUniversity) : "#"}
          className="rounded-lg border border-border px-3 py-1.5 text-sm font-medium hover:bg-surface"
        >
          📄 Export program brief (PDF)
        </a>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-[220px_1fr]">
        <div className="flex flex-col items-center justify-center rounded-xl border border-border bg-surface py-6">
          <ScoreDisplay score={score} />
          <div className="mt-1 text-xs text-muted">
            Weighted core coverage <InfoTip term="weighted_coverage" />
          </div>
        </div>
        <div className="text-sm">
          <p>
            This program covers approximately <strong>{score !== null ? Math.round(score) : "—"}%</strong> of the
            demand-weighted skills commonly required in{" "}
            <strong>{alignment?.relevant_roles ?? "general IT"}</strong> job postings in the Armenian IT market —
            skills employers ask for more often count for more.
          </p>
          <p className="mt-2 text-muted">
            Covers {alignment?.core_n_overlap ?? "—"} of {alignment?.core_n_job_skills ?? "—"} core skills (unweighted
            count) · {displayGaps.length} skills identified as gaps
          </p>
          <p className="mt-2 text-xs text-muted">
            📌 Relevant roles: {alignment?.relevant_roles ?? "unmapped"} <InfoTip term="relevant_roles" />
          </p>
          {doc_score < LOW_DOC_THRESHOLD && (
            <p className="mt-2 flex items-start gap-1.5 rounded-lg bg-orange-50 px-3 py-2 text-xs text-orange-800">
              📝 <span>
                This program&apos;s course descriptions are limited ({(doc_score * 100).toFixed(0)}% documentation
                quality) — the score above may understate this program because there wasn&apos;t much published
                course detail to analyze, not necessarily because the curriculum is weak.{" "}
                <InfoTip term="doc_score" />
              </span>
            </p>
          )}
        </div>
      </div>

      {benchmark && score !== null && (
        <>
          <h2 className="mt-8 text-base font-semibold">📊 How this compares</h2>
          <div className="mt-3 grid grid-cols-3 gap-4">
            <MetricCard label="This program" value={formatScore(score)} />
            <MetricCard label={<>Peer average (n={benchmark.peer_n}) <InfoTip term="peer_average" /></>} value={formatScore(benchmark.peer_mean)} />
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
        {(["strengths", "gaps", "evidence"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium ${
              tab === t ? "border-b-2 border-primary text-primary" : "text-muted"
            }`}
          >
            {t === "strengths" ? "✅ Strengths" : t === "gaps" ? "⚠️ Gaps" : "🔎 Course evidence"}
          </button>
        ))}
      </div>

      {tab === "strengths" && (
        <ul className="mt-4 space-y-2">
          {strengths.length === 0 && <p className="text-sm text-muted">No mapped role data for this program.</p>}
          {strengths.map((s) => {
            // The displayed skill name is the job-market's wording (e.g. "Distributed
            // Systems"), which can differ from the program's own course-skill wording
            // (e.g. "Distributed Computing Systems") when the match was semantic, not
            // exact — so course traceability is looked up via matched_program_skills,
            // not the displayed name itself.
            const rawCourses = (s.matched_program_skills ?? [s.skill]).flatMap((ps) => skill_courses[ps] ?? []);
            // Dedupe: the same course can teach more than one of a skill's
            // matched program-skill names.
            const courses = Array.from(
              rawCourses.reduce((byName, c) => {
                const existing = byName.get(c.course_name);
                byName.set(c.course_name, { course_name: c.course_name, high_confidence: (existing?.high_confidence ?? false) || c.high_confidence });
                return byName;
              }, new Map<string, { course_name: string; high_confidence: boolean }>()).values()
            );
            return (
              <li key={s.skill} className="rounded-lg border border-border px-3 py-2 text-sm">
                <details>
                  <summary className="flex cursor-pointer list-none items-center justify-between marker:content-none">
                    <span>
                      {s.skill}
                      {skillInfo[s.skill] && (
                        <TextTip
                          className="ml-1"
                          text={`${skillInfo[s.skill].description} Where it's used: ${skillInfo[s.skill].where_used}.`}
                        />
                      )}
                      {courses.length > 0 && (
                        <span className="ml-2 text-xs text-muted">▾ how was this decided?</span>
                      )}
                    </span>
                    <span className="text-xs text-muted">
                      {s.job_count} job postings
                      {s.pct_of_role_postings != null && ` (${s.pct_of_role_postings}%)`}
                    </span>
                  </summary>
                  {courses.length > 0 ? (
                    <ul className="mt-2 space-y-1 border-t border-border pt-2 text-xs text-muted">
                      {courses.map((c, i) => (
                        <li key={i}>
                          Taught in <strong>{c.course_name}</strong>
                          {c.high_confidence ? "" : " (weakly evidenced — short/generic course description)"}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-2 border-t border-border pt-2 text-xs text-muted">
                      No course-level detail available for this skill.
                    </p>
                  )}
                </details>
              </li>
            );
          })}
        </ul>
      )}

      {tab === "gaps" && (
        <div className="mt-4">
          {/* gap_type is a single program-wide estimate derived from this program's
              overall documentation quality (doc_score), not an independent judgment
              made on each gap below — a per-row badge stating it as such would be
              false precision. Individual skills only get their own classification
              when real per-skill category data exists (frozen historical runs);
              live-recomputed runs (the current default) don't have that, so most
              rows show no per-row badge at all — see the caveat banner instead. */}
          <Card className="mb-4 bg-surface">
            <p className="text-sm">
              📋 <strong>About these gaps:</strong> this program&apos;s course descriptions score{" "}
              {(doc_score * 100).toFixed(0)}% on documentation quality <InfoTip term="doc_score" />, so as a
              program-wide estimate these gaps are more likely to be{" "}
              <strong>{GAP_TYPE_LABELS[gap_type].toLowerCase()}</strong> ({GAP_TYPE_ICONS[gap_type]}). This is a
              program-level signal, not a verified judgment on each individual skill below.{" "}
              <InfoTip term="gap_type" />
            </p>
          </Card>
          <ul className="space-y-2">
            {displayGaps.map((g, i) => (
              <li key={i} className="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm">
                <span>
                  {g.category && `${GAP_TYPE_ICONS[g.category] ?? "⚪"} `}
                  {g.skill}
                  {skillInfo[g.skill] && (
                    <TextTip
                      className="ml-1"
                      text={`${skillInfo[g.skill].description} Where it's used: ${skillInfo[g.skill].where_used}.`}
                    />
                  )}
                </span>
                <span className="text-xs text-muted">
                  {g.freq ?? 0} job postings
                  {g.pct != null && ` (${g.pct}%)`}
                  {g.category && ` · ${GAP_TYPE_LABELS[g.category] ?? "Unclear"}`}
                </span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-xs text-muted">
            Documentation quality score for this program: {(doc_score * 100).toFixed(0)}% (proportion of extracted
            skills with high extraction confidence) <InfoTip term="doc_score" />
          </p>
        </div>
      )}

      {tab === "evidence" && (
        <div className="mt-4 space-y-6">
          <div>
            <h2 className="text-sm font-semibold">How to read this</h2>
            <p className="mt-1 text-xs text-muted">
              These are the skills currently extracted for each course. They are evidence for review, not a claim that
              every listed tool is taught in depth. Generated descriptions are clearly marked and do not replace an
              official syllabus.
            </p>
          </div>

          {program_outcomes.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold">Official program-level learning outcomes</h2>
              <p className="mt-1 text-xs text-muted">
                Program outcomes are shown separately and are not included in the alignment score yet.
              </p>
              <ul className="mt-3 space-y-2">
                {program_outcomes.map((outcome, i) => (
                  <li key={i} className="rounded-lg border border-border px-3 py-2 text-sm">
                    <p>{outcome.outcome_text}</p>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {outcome.skills.map((skill) => (
                        <span key={skill.skill_name} className="rounded bg-primary/10 px-2 py-0.5 text-xs text-primary-dark">
                          {skill.skill_name}
                        </span>
                      ))}
                    </div>
                    {outcome.source_url && (
                      <a href={outcome.source_url} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block text-xs text-primary hover:underline">
                        View official source →
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div>
            <h2 className="text-sm font-semibold">Course-level extracted skills ({course_evidence.length} courses)</h2>
            <ul className="mt-3 space-y-2">
              {course_evidence.map((course) => {
                const generated = course.notes?.includes("AI-generated");
                return (
                  <li key={course.course_name} className="rounded-lg border border-border px-3 py-2 text-sm">
                    <details>
                      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 marker:content-none">
                        <span>
                          <strong>{course.course_name}</strong>
                          {course.credits !== null && <span className="ml-2 text-xs text-muted">{course.credits} credits</span>}
                        </span>
                        <span className={`text-xs ${generated ? "text-orange-700" : "text-muted"}`}>
                          {generated ? "AI-generated description" : "Published source"} · {course.skills.length} skills ▾
                        </span>
                      </summary>
                      {course.description && <p className="mt-2 border-t border-border pt-2 text-xs text-muted">{course.description}</p>}
                      <div className="mt-2 flex flex-wrap gap-1">
                        {course.skills.map((skill) => (
                          <span key={skill.skill_name} className="rounded bg-surface px-2 py-0.5 text-xs text-primary-dark ring-1 ring-border">
                            {skill.skill_name}
                          </span>
                        ))}
                      </div>
                      {course.source_url && (
                        <a href={course.source_url} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block text-xs text-primary hover:underline">
                          View curriculum source →
                        </a>
                      )}
                    </details>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      )}

      <DataFreshnessNote meta={meta} />
    </div>
  );
}
