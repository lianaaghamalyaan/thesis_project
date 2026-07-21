"use client";

import { useEffect, useState } from "react";
import { api, JobFitResult, ProgramAlignment } from "@/lib/api";
import { ALL_UNIVERSITIES, useAuth } from "@/lib/auth-context";
import { DataFreshnessNote } from "@/components/DataFreshnessNote";
import { JobFitPanel } from "@/components/JobFitPanel";
import { ErrorState, PageHeader, PageSkeleton } from "@/components/ui";
import { useApi } from "@/lib/useApi";

export default function JobFitPage() {
  const { currentUniversity, universityParam, isAllUniversities, canSwitchUniversity, switchUniversity } = useAuth();
  const [program, setProgram] = useState("");
  const [degree, setDegree] = useState("");
  const [role, setRole] = useState("");
  const [result, setResult] = useState<JobFitResult | null>(null);
  const [fitError, setFitError] = useState<string | null>(null);

  const metaQ = useApi(() => api.runMetadata(), []);
  const universitiesQ = useApi(() => api.universities(), [], canSwitchUniversity && isAllUniversities);
  const programsQ = useApi(
    () => api.programs(universityParam),
    [universityParam],
    !!currentUniversity && !isAllUniversities
  );
  const rolesQ = useApi(() => api.jobFitRoles(), [], !isAllUniversities);
  const programs: ProgramAlignment[] = programsQ.data ?? [];
  const roles = rolesQ.data ?? [];

  // Keep the selected program valid for the loaded list. Critical when the
  // university switches: the previous university's program lingers in state
  // and, if it isn't in the new list, the <select> shows the first option
  // while state still holds the stale name — firing a job-fit request for a
  // program that doesn't exist at this university (returns 0/0). Reset to the
  // first program whenever the current selection isn't in the loaded set.
  const programValid = programs.some((p) => p.program === program && p.degree === degree);
  useEffect(() => {
    if (programs.length && !programValid) {
      setProgram(programs[0].program);
      setDegree(programs[0].degree);
    }
  }, [programs, programValid]);
  useEffect(() => {
    if (roles.length && !role) setRole(roles[0]);
  }, [roles, role]);

  useEffect(() => {
    // Only fetch once the program is confirmed to belong to this university —
    // never during the transient mismatch after a university switch.
    if (!(program && degree && role && universityParam && programValid)) return;
    let cancelled = false;
    setResult(null);
    setFitError(null);
    api
      .jobFit(program, degree, role, universityParam)
      .then((r) => {
        if (!cancelled) setResult(r);
      })
      .catch((e: unknown) => {
        if (!cancelled) setFitError(e instanceof Error ? e.message : "Request failed");
      });
    return () => {
      cancelled = true;
    };
  }, [program, degree, role, universityParam, programValid]);

  if (isAllUniversities) {
    return (
      <div>
        <PageHeader
          title="Job Fit"
          subtitle="Job Fit compares one specific program against a target role. Program names can repeat across universities, so pick a university first:"
        />
        <div className="mt-5 flex flex-wrap gap-2">
          {(universitiesQ.data ?? []).map((u) => (
            <button
              key={u}
              onClick={() => switchUniversity(u)}
              className="rounded-lg border border-border bg-surface px-3 py-2 text-sm font-medium hover:bg-surface-muted"
            >
              {u}
            </button>
          ))}
        </div>
        {universitiesQ.error && <ErrorState message={universitiesQ.error} onRetry={universitiesQ.retry} />}
      </div>
    );
  }

  if (programsQ.error) return <ErrorState message={programsQ.error} onRetry={programsQ.retry} />;
  if (!programsQ.data) return <PageSkeleton />;

  return (
    <div>
      <PageHeader title="Job Fit" subtitle="Compare a program directly against a specific target role." />

      <div className="mt-5">
        <label htmlFor="jobfit-program" className="mb-1 block text-xs font-medium text-muted">
          Program
        </label>
        <select
          id="jobfit-program"
          value={`${program}|${degree}`}
          onChange={(e) => {
            const [p, d] = e.target.value.split("|");
            setProgram(p);
            setDegree(d);
          }}
          className="min-w-64 rounded-lg border border-border bg-surface px-3 py-2 text-sm"
        >
          {programs.map((p) => (
            <option key={`${p.program}-${p.degree}`} value={`${p.program}|${p.degree}`}>
              {p.program} ({p.degree})
            </option>
          ))}
        </select>
      </div>

      <div className="mt-4">
        <div className="mb-1 text-xs font-medium text-muted">Target role</div>
        <div className="flex flex-wrap gap-2" role="tablist" aria-label="Target role">
          {roles.map((r) => (
            <button
              key={r}
              role="tab"
              aria-selected={role === r}
              onClick={() => setRole(r)}
              className={`rounded-full px-3 py-1.5 text-xs font-medium ring-1 ${
                role === r ? "bg-primary text-white ring-primary" : "bg-surface text-muted ring-border hover:bg-surface-muted"
              }`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {fitError && <ErrorState message={fitError} />}
      {!result && !fitError && program && role && <p className="mt-5 text-sm text-muted">Computing fit…</p>}
      {result && <JobFitPanel result={result} role={role} />}

      <DataFreshnessNote meta={metaQ.data} />
    </div>
  );
}
