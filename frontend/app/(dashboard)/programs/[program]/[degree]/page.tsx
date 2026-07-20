"use client";

import { Suspense, use, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  AlertTriangle,
  ArrowLeftRight,
  Briefcase,
  CheckCircle2,
  ChevronDown,
  ClipboardList,
  ExternalLink,
  FileDown,
  Pin,
  SearchCheck,
} from "lucide-react";
import { api, JobFitResult, ProgramAlignment, SkillInfo } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ScoreGauge } from "@/components/ScoreGauge";
import { MetricCard, Card } from "@/components/MetricCard";
import { InfoTip, TextTip } from "@/components/InfoTip";
import { DataFreshnessNote } from "@/components/DataFreshnessNote";
import { ErrorState, PageSkeleton, ScoreBar, TierLegend } from "@/components/ui";
import { formatScore, GAP_TYPE_ICONS, GAP_TYPE_LABELS } from "@/lib/format";
import { JobFitPanel } from "@/components/JobFitPanel";
import { useApi } from "@/lib/useApi";

const LOW_DOC_THRESHOLD = 0.25;

type TabId = "strengths" | "gaps" | "jobfit" | "evidence";

// Demand tiers for grouping gaps: pct = share of relevant-role postings
// demanding the skill.
const DEMAND_TIERS = [
  { id: "critical", label: "Critical demand", hint: "asked for in ≥ 30% of relevant postings", min: 30 },
  { id: "common", label: "Common demand", hint: "10–30% of relevant postings", min: 10 },
  { id: "niche", label: "Niche demand", hint: "under 10% of relevant postings", min: 0 },
] as const;

function ProgramDetailInner({ program, degree }: { program: string; degree: string }) {
  const { currentUniversity, universityParam } = useAuth();
  // A `?u=` query param pins the university explicitly — required in the
  // admin "All universities" mode, where the same program name + degree can
  // exist at two universities.
  const searchParams = useSearchParams();
  const pinnedUniversity = searchParams.get("u");
  const [tab, setTab] = useState<TabId>("strengths");
  const [skillInfo, setSkillInfo] = useState<Record<string, SkillInfo>>({});
  const [gapFilter, setGapFilter] = useState("");

  const metaQ = useApi(() => api.runMetadata(), []);
  const effectiveUniversity = pinnedUniversity ?? universityParam ?? null;

  const detailQ = useApi(
    () => api.programDetail(program, degree, effectiveUniversity ?? undefined),
    [program, degree, effectiveUniversity],
    !!currentUniversity && !!effectiveUniversity
  );
  const detail = detailQ.data;

  // Sibling degrees of the same program (Bachelor ↔ Master cross-link).
  const programsQ = useApi(
    () => api.programs(effectiveUniversity ?? undefined),
    [effectiveUniversity],
    !!currentUniversity && !!effectiveUniversity
  );
  const siblings = useMemo(
    () =>
      (programsQ.data ?? []).filter(
        (p) => p.program === program && p.degree !== degree && (!effectiveUniversity || p.university === effectiveUniversity)
      ),
    [programsQ.data, program, degree, effectiveUniversity]
  );

  // Job Fit tab state
  const rolesQ = useApi(() => api.jobFitRoles(), []);
  const [fitRole, setFitRole] = useState<string | null>(null);
  const [fitResult, setFitResult] = useState<JobFitResult | null>(null);
  const [fitError, setFitError] = useState<string | null>(null);
  useEffect(() => {
    if (tab !== "jobfit" || !fitRole || !effectiveUniversity) return;
    setFitResult(null);
    setFitError(null);
    api
      .jobFit(program, degree, fitRole, effectiveUniversity)
      .then(setFitResult)
      .catch((e: unknown) => setFitError(e instanceof Error ? e.message : "Request failed"));
  }, [tab, fitRole, program, degree, effectiveUniversity]);
  useEffect(() => {
    if (rolesQ.data?.length && !fitRole) setFitRole(rolesQ.data[0]);
  }, [rolesQ.data, fitRole]);

  const allSkillNames = useMemo(() => {
    if (!detail) return [];
    const gapNames = detail.gaps.length
      ? detail.gaps.map((g) => g.missing_skill)
      : detail.fallback_gaps.map((g) => g.gap_skill);
    return Array.from(new Set([...detail.strengths.map((s) => s.skill), ...gapNames]));
  }, [detail]);

  useEffect(() => {
    if (allSkillNames.length === 0) return;
    api.skillsInfo(allSkillNames).then(setSkillInfo).catch(() => {});
  }, [allSkillNames]);

  if (detailQ.error) return <ErrorState message={detailQ.error} onRetry={detailQ.retry} />;
  if (!detail) return <PageSkeleton />;

  const { alignment, gaps, fallback_gaps, strengths, skill_courses, benchmark, doc_score, gap_type, course_evidence, program_outcomes } = detail;
  // weighted_core_coverage_pct is the headline metric (frequency-weighted,
  // so high-demand skills dominate).
  const score = alignment?.weighted_core_coverage_pct ?? null;
  const displayGaps = gaps.length
    ? gaps.map((g) => ({ skill: g.missing_skill, freq: g.job_frequency, pct: g.pct_of_role_postings, category: g.category }))
    : fallback_gaps.map((g) => ({ skill: g.gap_skill, freq: g.job_frequency, pct: g.pct_of_role_postings, category: null }));

  const filteredGaps = displayGaps.filter((g) => g.skill.toLowerCase().includes(gapFilter.toLowerCase()));
  const gapsByTier = DEMAND_TIERS.map((tier, i) => {
    const max = i === 0 ? Infinity : DEMAND_TIERS[i - 1].min;
    return {
      ...tier,
      rows: filteredGaps.filter((g) => {
        const pct = g.pct ?? 0;
        return pct >= tier.min && pct < max;
      }),
    };
  });
  const maxGapPct = Math.max(1, ...filteredGaps.map((g) => g.pct ?? 0));

  const TABS: { id: TabId; label: string; icon: React.ReactNode }[] = [
    { id: "strengths", label: `Strengths (${strengths.length})`, icon: <CheckCircle2 className="h-4 w-4" aria-hidden /> },
    { id: "gaps", label: `Gaps (${displayGaps.length})`, icon: <AlertTriangle className="h-4 w-4" aria-hidden /> },
    { id: "jobfit", label: "Job Fit", icon: <Briefcase className="h-4 w-4" aria-hidden /> },
    { id: "evidence", label: "Course evidence", icon: <SearchCheck className="h-4 w-4" aria-hidden /> },
  ];

  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold text-primary-dark">{program}</h1>
          <p className="mt-1 text-sm text-muted">
            {degree} · {effectiveUniversity}
          </p>
          <div className="mt-1 flex flex-wrap items-center gap-3 text-sm">
            {alignment?.source_url && (
              <a
                href={alignment.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 font-medium text-primary hover:underline"
              >
                <ExternalLink className="h-3.5 w-3.5" aria-hidden /> Official curriculum
              </a>
            )}
            {siblings.map((s) => (
              <Link
                key={s.degree}
                href={`/programs/${encodeURIComponent(s.program)}/${encodeURIComponent(s.degree)}?u=${encodeURIComponent(s.university)}`}
                className="inline-flex items-center gap-1 font-medium text-primary hover:underline"
              >
                <ArrowLeftRight className="h-3.5 w-3.5" aria-hidden /> Compare with the {s.degree} program ({formatScore(s.weighted_core_coverage_pct)})
              </Link>
            ))}
          </div>
        </div>
        <a
          href={effectiveUniversity ? api.programBriefPdfUrl(program, degree, effectiveUniversity) : "#"}
          className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-border bg-surface px-3 py-1.5 text-sm font-medium hover:bg-surface-muted"
        >
          <FileDown className="h-4 w-4" aria-hidden /> Program brief (PDF)
        </a>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-[220px_1fr]">
        <div className="flex flex-col items-center justify-center rounded-xl bg-surface py-6 shadow-card ring-1 ring-border/60">
          <ScoreGauge score={score} />
          <div className="mt-2 text-xs text-muted">
            Market alignment score <InfoTip term="weighted_coverage" />
          </div>
        </div>
        <div className="text-sm leading-relaxed">
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
          <p className="mt-2 inline-flex items-center gap-1.5 text-xs text-muted">
            <Pin className="h-3.5 w-3.5" aria-hidden /> Relevant roles: {alignment?.relevant_roles ?? "unmapped"}{" "}
            <InfoTip term="relevant_roles" />
          </p>
          <TierLegend className="mt-2" />
          {doc_score < LOW_DOC_THRESHOLD && (
            <p className="mt-2 flex items-start gap-1.5 rounded-lg bg-orange-50 px-3 py-2 text-xs text-orange-800">
              <ClipboardList className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden />
              <span>
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
          <h2 className="mt-8 text-base font-semibold">How this compares</h2>
          <div className="mt-3 grid grid-cols-3 gap-4">
            <MetricCard label="This program" value={formatScore(score)} />
            <MetricCard label={<>Peer average (n={benchmark.peer_n}) <InfoTip term="peer_average" /></>} value={formatScore(benchmark.peer_mean)} />
            <MetricCard
              label="Difference"
              value={`${score - benchmark.peer_mean >= 0 ? "+" : ""}${Math.round(score - benchmark.peer_mean)} pts`}
            />
          </div>
          <p className="mt-2 text-xs text-muted">
            Compared against {benchmark.peer_n} programs at other Armenian universities, matched by{" "}
            {benchmark.matched_on}. Peer best observed: {formatScore(benchmark.peer_max)}.
          </p>
        </>
      )}

      <hr className="my-6 border-border" />

      <div className="flex gap-1 border-b border-border" role="tablist">
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            onClick={() => setTab(t.id)}
            className={`inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium ${
              tab === t.id ? "border-b-2 border-primary text-primary" : "text-muted hover:text-foreground"
            }`}
          >
            {t.icon}
            {t.label}
          </button>
        ))}
      </div>

      {tab === "strengths" && (
        <ul className="mt-4 space-y-2">
          {strengths.length === 0 && <p className="text-sm text-muted">No mapped role data for this program.</p>}
          {strengths.map((s) => {
            // The displayed skill name is the job-market's wording, which can
            // differ from the program's own course-skill wording when the match
            // was semantic — so course traceability is looked up via
            // matched_program_skills, not the displayed name itself.
            const rawCourses = (s.matched_program_skills ?? [s.skill]).flatMap((ps) => skill_courses[ps] ?? []);
            const courses = Array.from(
              rawCourses.reduce((byName, c) => {
                const existing = byName.get(c.course_name);
                byName.set(c.course_name, { course_name: c.course_name, high_confidence: (existing?.high_confidence ?? false) || c.high_confidence });
                return byName;
              }, new Map<string, { course_name: string; high_confidence: boolean }>()).values()
            );
            return (
              <li key={s.skill} className="rounded-lg border border-border bg-surface px-3 py-2 text-sm">
                <details className="group">
                  <summary className="flex cursor-pointer list-none items-center justify-between marker:content-none">
                    <span className="inline-flex items-center">
                      {s.skill}
                      {skillInfo[s.skill] && (
                        <TextTip
                          className="ml-1"
                          text={`${skillInfo[s.skill].description} Where it's used: ${skillInfo[s.skill].where_used}.`}
                        />
                      )}
                      {courses.length > 0 && (
                        <span className="ml-2 inline-flex items-center gap-0.5 text-xs text-muted">
                          <ChevronDown className="h-3 w-3 transition-transform group-open:rotate-180" aria-hidden />
                          how was this decided?
                        </span>
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
              made on each gap below. */}
          <Card className="mb-4">
            <p className="text-sm leading-relaxed">
              <strong>About these gaps:</strong> this program&apos;s course descriptions score{" "}
              {(doc_score * 100).toFixed(0)}% on documentation quality <InfoTip term="doc_score" />, so as a
              program-wide estimate these gaps are more likely to be{" "}
              <strong>{GAP_TYPE_LABELS[gap_type].toLowerCase()}</strong> ({GAP_TYPE_ICONS[gap_type]}). This is a
              program-level signal, not a verified judgment on each individual skill below.{" "}
              <InfoTip term="gap_type" />
            </p>
          </Card>

          <input
            type="search"
            value={gapFilter}
            onChange={(e) => setGapFilter(e.target.value)}
            placeholder="Filter gap skills…"
            aria-label="Filter gap skills"
            className="mb-4 w-full max-w-xs rounded-lg border border-border bg-surface px-3 py-2 text-sm"
          />

          {gapsByTier.map(
            (tier) =>
              tier.rows.length > 0 && (
                <div key={tier.id} className="mb-5">
                  <h3 className="text-sm font-semibold">
                    {tier.label} <span className="font-normal text-muted">— {tier.hint} · {tier.rows.length} skills</span>
                  </h3>
                  <ul className="mt-2 space-y-2">
                    {tier.rows.map((g, i) => (
                      <li key={i} className="flex items-center justify-between gap-4 rounded-lg border border-border bg-surface px-3 py-2 text-sm">
                        <span className="inline-flex min-w-0 items-center">
                          {g.category && `${GAP_TYPE_ICONS[g.category] ?? "⚪"} `}
                          <span className="truncate">{g.skill}</span>
                          {skillInfo[g.skill] && (
                            <TextTip
                              className="ml-1"
                              text={`${skillInfo[g.skill].description} Where it's used: ${skillInfo[g.skill].where_used}.`}
                            />
                          )}
                        </span>
                        <span className="flex shrink-0 items-center gap-3 text-xs text-muted">
                          <span className="hidden h-1.5 w-24 overflow-hidden rounded-full bg-surface-muted sm:block" aria-hidden>
                            <span
                              className="block h-full rounded-full bg-primary/70"
                              style={{ width: `${((g.pct ?? 0) / maxGapPct) * 100}%` }}
                            />
                          </span>
                          {g.freq ?? 0} postings
                          {g.pct != null && ` (${g.pct}%)`}
                          {g.category && ` · ${GAP_TYPE_LABELS[g.category] ?? "Unclear"}`}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )
          )}
          {filteredGaps.length === 0 && <p className="text-sm text-muted">No gap skills match this filter.</p>}

          <p className="mt-4 text-xs text-muted">
            Documentation quality score for this program: {(doc_score * 100).toFixed(0)}% (proportion of extracted
            skills with high extraction confidence) <InfoTip term="doc_score" />
          </p>
        </div>
      )}

      {tab === "jobfit" && (
        <div className="mt-4">
          <p className="text-sm text-muted">
            How well does <strong className="text-foreground">{program} ({degree})</strong> prepare graduates for a
            specific role? Pick a target role:
          </p>
          <div className="mt-3 flex flex-wrap gap-2" role="tablist" aria-label="Target role">
            {(rolesQ.data ?? []).map((r) => (
              <button
                key={r}
                role="tab"
                aria-selected={fitRole === r}
                onClick={() => setFitRole(r)}
                className={`rounded-full px-3 py-1.5 text-xs font-medium ring-1 ${
                  fitRole === r ? "bg-primary text-white ring-primary" : "bg-surface text-muted ring-border hover:bg-surface-muted"
                }`}
              >
                {r}
              </button>
            ))}
          </div>

          {fitError && <ErrorState message={fitError} />}
          {!fitResult && !fitError && fitRole && <p className="mt-4 text-sm text-muted">Computing fit…</p>}

          {fitResult && (
            <JobFitPanel result={fitResult} role={fitRole ?? ""} />
          )}
        </div>
      )}

      {tab === "evidence" && (
        <div className="mt-4 space-y-6">
          <div>
            <h2 className="text-sm font-semibold">How to read this</h2>
            <p className="mt-1 max-w-3xl text-xs leading-relaxed text-muted">
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
                  <li key={i} className="rounded-lg border border-border bg-surface px-3 py-2 text-sm">
                    <p>{outcome.outcome_text}</p>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {outcome.skills.map((skill) => (
                        <span key={skill.skill_name} className="rounded bg-primary-50 px-2 py-0.5 text-xs text-primary-dark">
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
                  <li key={course.course_name} className="rounded-lg border border-border bg-surface px-3 py-2 text-sm">
                    <details className="group">
                      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 marker:content-none">
                        <span>
                          <strong>{course.course_name}</strong>
                          {course.credits !== null && <span className="ml-2 text-xs text-muted">{course.credits} credits</span>}
                        </span>
                        <span className={`inline-flex items-center gap-1 text-xs ${generated ? "text-orange-700" : "text-muted"}`}>
                          {generated ? "AI-generated description" : "Published source"} · {course.skills.length} skills
                          <ChevronDown className="h-3 w-3 transition-transform group-open:rotate-180" aria-hidden />
                        </span>
                      </summary>
                      {course.description && <p className="mt-2 border-t border-border pt-2 text-xs leading-relaxed text-muted">{course.description}</p>}
                      <div className="mt-2 flex flex-wrap gap-1">
                        {course.skills.map((skill) => (
                          <span key={skill.skill_name} className="rounded bg-surface-muted px-2 py-0.5 text-xs text-primary-dark ring-1 ring-border">
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

      <DataFreshnessNote meta={metaQ.data} />
    </div>
  );
}

export default function ProgramDetailPage({
  params,
}: {
  params: Promise<{ program: string; degree: string }>;
}) {
  const { program: rawProgram, degree: rawDegree } = use(params);
  return (
    <Suspense fallback={<PageSkeleton />}>
      <ProgramDetailInner program={decodeURIComponent(rawProgram)} degree={decodeURIComponent(rawDegree)} />
    </Suspense>
  );
}
