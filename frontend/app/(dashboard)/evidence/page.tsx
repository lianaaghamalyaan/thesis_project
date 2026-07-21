"use client";

import { useEffect, useState } from "react";
import { Briefcase, ChevronDown, Database, ExternalLink, GraduationCap, Quote } from "lucide-react";
import { api, EvidenceCourse, EvidenceMeta, EvidencePosting } from "@/lib/api";
import { EmptyState, ErrorState, PageHeader, PageSkeleton } from "@/components/ui";
import { formatDate } from "@/lib/format";
import { useApi } from "@/lib/useApi";

const PAGE = 25;

export default function EvidencePage() {
  const [tab, setTab] = useState<"jobs" | "courses">("jobs");
  const metaQ = useApi<EvidenceMeta>(() => api.evidenceMeta(), []);

  // Job side
  const [jobQ, setJobQ] = useState("");
  const [jobRole, setJobRole] = useState("");
  const [jobSource, setJobSource] = useState("");
  const [postings, setPostings] = useState<EvidencePosting[]>([]);
  const [jobTotal, setJobTotal] = useState(0);
  const [jobError, setJobError] = useState<string | null>(null);
  const [jobLoading, setJobLoading] = useState(false);

  // Course side
  const [courseQ, setCourseQ] = useState("");
  const [courseUni, setCourseUni] = useState("");
  const [courseProgram, setCourseProgram] = useState("");
  const [courses, setCourses] = useState<EvidenceCourse[]>([]);
  const [courseTotal, setCourseTotal] = useState(0);
  const [courseError, setCourseError] = useState<string | null>(null);
  const [courseLoading, setCourseLoading] = useState(false);

  const loadJobs = (offset: number) => {
    setJobLoading(true);
    setJobError(null);
    api
      .evidenceJobs({ q: jobQ, role: jobRole, source: jobSource, offset, limit: PAGE })
      .then((r) => {
        setJobTotal(r.total);
        setPostings((prev) => (offset === 0 ? r.postings : [...prev, ...r.postings]));
      })
      .catch((e: unknown) => setJobError(e instanceof Error ? e.message : "Request failed"))
      .finally(() => setJobLoading(false));
  };

  const loadCourses = (offset: number) => {
    setCourseLoading(true);
    setCourseError(null);
    api
      .evidenceCourses({ q: courseQ, university: courseUni, program: courseProgram, offset, limit: PAGE })
      .then((r) => {
        setCourseTotal(r.total);
        setCourses((prev) => (offset === 0 ? r.courses : [...prev, ...r.courses]));
      })
      .catch((e: unknown) => setCourseError(e instanceof Error ? e.message : "Request failed"))
      .finally(() => setCourseLoading(false));
  };

  // Debounced refetch on filter change.
  useEffect(() => {
    const t = setTimeout(() => loadJobs(0), 350);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobQ, jobRole, jobSource]);

  useEffect(() => {
    const t = setTimeout(() => loadCourses(0), 350);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseQ, courseUni, courseProgram]);

  // Clearing/switching the university resets the program filter, since the
  // program list is scoped to the chosen university.
  useEffect(() => {
    setCourseProgram("");
  }, [courseUni]);

  if (metaQ.error) return <ErrorState message={metaQ.error} onRetry={metaQ.retry} />;
  if (!metaQ.data) return <PageSkeleton />;
  const meta = metaQ.data;

  return (
    <div>
      <PageHeader
        title="Evidence Explorer"
        subtitle="Every score in this dashboard is computed from the records below — nothing else. Browse the job postings with each extracted skill and the exact phrase it came from, and the courses with the skills extracted from their descriptions."
      />

      {meta.extraction_run && (
        <p className="mt-3 inline-flex flex-wrap items-center gap-x-2 rounded-lg bg-primary-50 px-3 py-2 text-xs text-muted">
          <Database className="h-3.5 w-3.5 text-primary" aria-hidden />
          Job-skill extraction run <span className="font-mono text-foreground">{meta.extraction_run.run_key}</span>
          · model <span className="font-mono text-foreground">{meta.extraction_run.model_name}</span>
          · prompt <span className="font-mono text-foreground">{meta.extraction_run.prompt_version}</span>
          {meta.extraction_run.completed_at && <>· completed {formatDate(meta.extraction_run.completed_at)}</>}
        </p>
      )}

      <div className="mt-5 flex gap-1 border-b border-border" role="tablist">
        {(
          [
            { id: "jobs", label: "Job postings", icon: <Briefcase className="h-4 w-4" aria-hidden /> },
            { id: "courses", label: "Courses", icon: <GraduationCap className="h-4 w-4" aria-hidden /> },
          ] as const
        ).map((t) => (
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

      {tab === "jobs" && (
        <div className="mt-4">
          <div className="flex flex-wrap gap-3">
            <select value={jobRole} onChange={(e) => setJobRole(e.target.value)} aria-label="Filter by role group" className="rounded-lg border border-border bg-surface px-3 py-2 text-sm">
              <option value="">All role groups</option>
              {meta.role_groups.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
            <select value={jobSource} onChange={(e) => setJobSource(e.target.value)} aria-label="Filter by source" className="rounded-lg border border-border bg-surface px-3 py-2 text-sm">
              <option value="">All sources</option>
              {meta.sources.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <input
              type="search"
              value={jobQ}
              onChange={(e) => setJobQ(e.target.value)}
              placeholder="Search title, company, or skill (e.g. Kafka)…"
              aria-label="Search postings"
              className="min-w-72 flex-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm"
            />
          </div>
          {jobError && <ErrorState message={jobError} onRetry={() => loadJobs(0)} />}
          <p className="mt-3 text-xs text-muted">{jobTotal} postings match · showing {postings.length}</p>

          <ul className="mt-3 space-y-2">
            {postings.map((p) => (
              <li key={p.posting_id} className="rounded-lg border border-border bg-surface px-4 py-3 text-sm">
                <details className="group">
                  <summary className="flex cursor-pointer list-none items-start justify-between gap-3 marker:content-none">
                    <span>
                      <span className="font-semibold">{p.job_title}</span>
                      {p.company_name && <span className="text-muted"> · {p.company_name}</span>}
                      <span className="mt-0.5 block text-xs text-muted">
                        {[p.it_role_group, p.seniority_level, p.location, p.posting_date && formatDate(p.posting_date)]
                          .filter(Boolean)
                          .join(" · ")}{" "}
                        · via {p.source_name}
                      </span>
                    </span>
                    <span className="inline-flex shrink-0 items-center gap-1 text-xs text-muted">
                      {p.skills.length} skills
                      <ChevronDown className="h-3.5 w-3.5 transition-transform group-open:rotate-180" aria-hidden />
                    </span>
                  </summary>
                  <div className="mt-3 space-y-2 border-t border-border pt-3">
                    {p.skills.map((s) => (
                      <div key={s.skill_name} className="text-xs">
                        <span className="font-medium text-foreground">{s.skill_name}</span>
                        {s.raw_skill_name !== s.skill_name && (
                          <span className="text-muted"> (extracted as &ldquo;{s.raw_skill_name}&rdquo;)</span>
                        )}
                        {s.evidence_type !== "explicit" && (
                          <span className="ml-1 rounded-full bg-amber-50 px-1.5 py-0.5 text-[10px] text-amber-700 ring-1 ring-amber-200">{s.evidence_type}</span>
                        )}
                        <span className="mt-0.5 flex items-start gap-1 text-muted">
                          <Quote className="mt-0.5 h-3 w-3 shrink-0 text-accent" aria-hidden />
                          <span className="italic">{s.evidence_text}</span>
                        </span>
                      </div>
                    ))}
                    {p.skills.length === 0 && <p className="text-xs text-muted">No skills extracted for this posting in the current run.</p>}
                    <a href={p.source_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline">
                      <ExternalLink className="h-3 w-3" aria-hidden /> Original posting
                    </a>
                  </div>
                </details>
              </li>
            ))}
          </ul>
          {postings.length === 0 && !jobLoading && !jobError && (
            <EmptyState title="No postings match" hint="Try a different search term or clear the filters." />
          )}
          {postings.length < jobTotal && (
            <button
              onClick={() => loadJobs(postings.length)}
              disabled={jobLoading}
              className="mt-4 rounded-lg border border-border bg-surface px-4 py-2 text-sm font-medium hover:bg-surface-muted disabled:opacity-50"
            >
              {jobLoading ? "Loading…" : `Load ${Math.min(PAGE, jobTotal - postings.length)} more`}
            </button>
          )}
        </div>
      )}

      {tab === "courses" && (
        <div className="mt-4">
          <div className="flex flex-wrap gap-3">
            <select value={courseUni} onChange={(e) => setCourseUni(e.target.value)} aria-label="Filter by university" className="rounded-lg border border-border bg-surface px-3 py-2 text-sm">
              <option value="">All universities</option>
              {meta.universities.map((u) => (
                <option key={u} value={u}>{u}</option>
              ))}
            </select>
            {courseUni && (meta.programs_by_university[courseUni]?.length ?? 0) > 0 && (
              <select value={courseProgram} onChange={(e) => setCourseProgram(e.target.value)} aria-label="Filter by program" className="rounded-lg border border-border bg-surface px-3 py-2 text-sm">
                <option value="">All programs</option>
                {meta.programs_by_university[courseUni].map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            )}
            <input
              type="search"
              value={courseQ}
              onChange={(e) => setCourseQ(e.target.value)}
              placeholder="Search course, program, or skill…"
              aria-label="Search courses"
              className="min-w-72 flex-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm"
            />
          </div>
          {courseError && <ErrorState message={courseError} onRetry={() => loadCourses(0)} />}
          <p className="mt-3 text-xs text-muted">{courseTotal} courses match · showing {courses.length}</p>

          <ul className="mt-3 space-y-2">
            {courses.map((c) => (
              <li key={c.course_id} className="rounded-lg border border-border bg-surface px-4 py-3 text-sm">
                <details className="group">
                  <summary className="flex cursor-pointer list-none items-start justify-between gap-3 marker:content-none">
                    <span>
                      <span className="font-semibold">{c.course_name}</span>
                      {c.credits !== null && <span className="text-xs text-muted"> · {c.credits} credits</span>}
                      <span className="mt-0.5 block text-xs text-muted">
                        {c.university} · {c.program} ({c.degree})
                      </span>
                    </span>
                    <span className="inline-flex shrink-0 items-center gap-1 text-xs text-muted">
                      {c.ai_generated && (
                        <span className="rounded-full bg-orange-50 px-1.5 py-0.5 text-[10px] text-orange-700 ring-1 ring-orange-200">AI-generated description</span>
                      )}
                      {c.skills.length} skills
                      <ChevronDown className="h-3.5 w-3.5 transition-transform group-open:rotate-180" aria-hidden />
                    </span>
                  </summary>
                  <div className="mt-3 space-y-2 border-t border-border pt-3">
                    {c.description && <p className="text-xs leading-relaxed text-muted">{c.description}</p>}
                    <div className="flex flex-wrap gap-1">
                      {c.skills.map((s) => (
                        <span
                          key={s.skill_name}
                          title={`Extraction: ${s.extraction_method} from ${s.input_type}${s.confidence_tier ? ` · confidence: ${s.confidence_tier}` : ""}`}
                          className={`cursor-help rounded px-2 py-0.5 text-xs ring-1 ${
                            s.confidence_tier === "low"
                              ? "bg-amber-50 text-amber-800 ring-amber-200"
                              : "bg-surface-muted text-primary-dark ring-border"
                          }`}
                        >
                          {s.skill_name}
                        </span>
                      ))}
                    </div>
                    {c.source_url && (
                      <a href={c.source_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline">
                        <ExternalLink className="h-3 w-3" aria-hidden /> Curriculum source
                      </a>
                    )}
                  </div>
                </details>
              </li>
            ))}
          </ul>
          {courses.length === 0 && !courseLoading && !courseError && (
            <EmptyState title="No courses match" hint="Try a different search term or clear the filters." />
          )}
          {courses.length < courseTotal && (
            <button
              onClick={() => loadCourses(courses.length)}
              disabled={courseLoading}
              className="mt-4 rounded-lg border border-border bg-surface px-4 py-2 text-sm font-medium hover:bg-surface-muted disabled:opacity-50"
            >
              {courseLoading ? "Loading…" : `Load ${Math.min(PAGE, courseTotal - courses.length)} more`}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
