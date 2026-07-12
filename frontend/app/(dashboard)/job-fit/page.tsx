"use client";

import { useEffect, useState } from "react";
import { api, JobFitResult, ProgramAlignment, RunMetadata } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { InfoTip } from "@/components/InfoTip";
import { DataFreshnessNote } from "@/components/DataFreshnessNote";
import { formatScore, scoreColor } from "@/lib/format";

export default function JobFitPage() {
  const { currentUniversity, universityParam, isAllUniversities } = useAuth();
  const [programs, setPrograms] = useState<ProgramAlignment[]>([]);
  const [roles, setRoles] = useState<string[]>([]);
  const [program, setProgram] = useState("");
  const [degree, setDegree] = useState("");
  const [role, setRole] = useState("");
  const [result, setResult] = useState<JobFitResult | null>(null);
  const [meta, setMeta] = useState<RunMetadata | null>(null);

  useEffect(() => {
    api.runMetadata().then(setMeta);
  }, []);

  useEffect(() => {
    if (!currentUniversity || isAllUniversities) return;
    api.programs(universityParam).then((p) => {
      setPrograms(p);
      if (p.length) {
        setProgram(p[0].program);
        setDegree(p[0].degree);
      }
    });
    api.jobFitRoles().then((r) => {
      setRoles(r);
      if (r.length) setRole(r[0]);
    });
  }, [currentUniversity, universityParam, isAllUniversities]);

  useEffect(() => {
    if (program && degree && role && universityParam) {
      setResult(null);
      api.jobFit(program, degree, role, universityParam).then(setResult);
    }
  }, [program, degree, role, universityParam]);

  if (isAllUniversities) {
    return (
      <div>
        <h1 className="text-3xl font-bold text-primary-dark">Job Fit</h1>
        <p className="mt-4 rounded-lg bg-surface px-4 py-3 text-sm text-muted">
          Job Fit compares one specific program against a target role — select a specific university in the banner
          above to use it. (Program names can repeat across universities, so an "all universities" comparison would
          be ambiguous.)
        </p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-primary-dark">Job Fit</h1>
      <p className="mt-1 text-sm text-muted">Compare a program directly against a specific target role.</p>

      <div className="mt-5 flex flex-wrap gap-3">
        <select
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
        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="min-w-48 rounded-lg border border-border bg-surface px-3 py-2 text-sm"
        >
          {roles.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </div>

      {result && (
        <>
          <div className="mt-6 flex items-center gap-6 rounded-xl border border-border bg-surface p-5">
            <div className="text-center">
              <div className="text-4xl font-bold" style={{ color: scoreColor(result.match_score) }}>
                {formatScore(result.match_score)}
              </div>
              <div className="text-xs text-muted">
                core skills covered <InfoTip term="core_coverage" />
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-semibold" style={{ color: scoreColor(result.weighted_score) }}>
                {formatScore(result.weighted_score)}
              </div>
              <div className="text-xs text-muted">
                frequency-weighted <InfoTip term="weighted_coverage" />
              </div>
            </div>
            <div className="text-sm text-muted">
              Covers {result.n_core_skills - result.missing.length} of <strong>{result.n_core_skills} core skills</strong>{" "}
              for <strong>{role}</strong> — skills demanded in at least 5% of the role's {result.n_role_postings}{" "}
              postings. Same matching methodology as the program alignment scores, so these numbers are directly
              comparable to a program's headline score.
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
            <div>
              <h2 className="text-base font-semibold">✅ Covered skills</h2>
              <p className="text-xs text-muted">Role-demanded skills this program covers (★ = core skill).</p>
              <ul className="mt-3 space-y-1">
                {result.matched.slice(0, 25).map((s) => (
                  <li key={s.skill} className="flex justify-between rounded-lg border border-border px-3 py-1.5 text-sm">
                    <span>
                      {s.is_core ? "★ " : ""}
                      {s.skill}
                    </span>
                    <span className="text-xs text-muted">{s.job_count} postings</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h2 className="text-base font-semibold">⚠️ Missing core skills</h2>
              <p className="text-xs text-muted">High-demand skills for this role that the program doesn't cover.</p>
              <ul className="mt-3 space-y-1">
                {result.missing.map((s) => (
                  <li key={s.skill} className="flex justify-between rounded-lg border border-border px-3 py-1.5 text-sm">
                    <span>{s.skill}</span>
                    <span className="text-xs text-muted">{s.job_count} postings</span>
                  </li>
                ))}
                {result.missing.length === 0 && (
                  <p className="text-sm text-muted">No core gaps — the program covers every core skill for this role.</p>
                )}
              </ul>
            </div>
          </div>
        </>
      )}

      <DataFreshnessNote meta={meta} />
    </div>
  );
}
