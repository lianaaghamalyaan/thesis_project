"use client";

import { useEffect, useState } from "react";
import { api, JobFitResult, ProgramAlignment } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { formatScore, scoreColor } from "@/lib/format";

export default function JobFitPage() {
  const { currentUniversity } = useAuth();
  const [programs, setPrograms] = useState<ProgramAlignment[]>([]);
  const [roles, setRoles] = useState<string[]>([]);
  const [program, setProgram] = useState("");
  const [degree, setDegree] = useState("");
  const [role, setRole] = useState("");
  const [result, setResult] = useState<JobFitResult | null>(null);

  useEffect(() => {
    if (!currentUniversity) return;
    api.programs(currentUniversity).then((p) => {
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
  }, [currentUniversity]);

  useEffect(() => {
    if (program && degree && role && currentUniversity) {
      api.jobFit(program, degree, role, currentUniversity).then(setResult);
    }
  }, [program, degree, role, currentUniversity]);

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
          <div className="mt-6 flex items-center gap-4 rounded-xl border border-border bg-surface p-5">
            <div className="text-4xl font-bold" style={{ color: scoreColor(result.match_score) }}>
              {formatScore(result.match_score)}
            </div>
            <div className="text-sm text-muted">
              Match score against <strong>{role}</strong> — {result.n_program_skills} program skills vs.{" "}
              {result.n_role_skills} role-demanded skills.
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
            <div>
              <h2 className="text-base font-semibold">✅ Matched skills</h2>
              <ul className="mt-3 space-y-1">
                {result.matched.slice(0, 20).map((s) => (
                  <li key={s.skill} className="flex justify-between rounded-lg border border-border px-3 py-1.5 text-sm">
                    <span>{s.skill}</span>
                    <span className="text-xs text-muted">{s.job_count} postings</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h2 className="text-base font-semibold">⚠️ Missing skills</h2>
              <ul className="mt-3 space-y-1">
                {result.missing.slice(0, 20).map((s) => (
                  <li key={s.skill} className="flex justify-between rounded-lg border border-border px-3 py-1.5 text-sm">
                    <span>{s.skill}</span>
                    <span className="text-xs text-muted">{s.job_count} postings</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
