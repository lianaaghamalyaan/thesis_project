"use client";

import { AlertTriangle, CheckCircle2 } from "lucide-react";
import { JobFitResult } from "@/lib/api";
import { InfoTip } from "@/components/InfoTip";
import { formatScore, scoreColor } from "@/lib/format";

/** Shared Job Fit result panel (also used by the standalone Job Fit page). */
export function JobFitPanel({ result, role }: { result: JobFitResult; role: string }) {
  const covered = result.n_core_skills - result.missing.length;
  return (
    <>
      <div className="mt-5 flex flex-wrap items-center gap-6 rounded-xl bg-surface p-5 shadow-card ring-1 ring-border/60">
        <div className="text-center">
          <div className="font-display text-4xl font-bold" style={{ color: scoreColor(result.weighted_score) }}>
            {formatScore(result.weighted_score)}
          </div>
          <div className="text-xs text-muted">
            market alignment (demand-weighted) <InfoTip term="weighted_coverage" />
          </div>
        </div>
        <div className="text-center">
          <div className="font-display text-2xl font-semibold" style={{ color: scoreColor(result.match_score) }}>
            {formatScore(result.match_score)}
          </div>
          <div className="text-xs text-muted">
            core skills covered (unweighted) <InfoTip term="core_coverage" />
          </div>
        </div>
        <div className="min-w-56 flex-1 text-sm leading-relaxed text-muted">
          <div className="mb-1.5 flex h-2 w-full overflow-hidden rounded-full bg-surface-muted" aria-hidden>
            <span className="h-full bg-score-strong" style={{ width: `${(covered / Math.max(result.n_core_skills, 1)) * 100}%` }} />
          </div>
          Covers <strong className="text-foreground">{covered} of {result.n_core_skills} core skills</strong> for{" "}
          <strong className="text-foreground">{role}</strong> — skills demanded in at least 5% of the role&apos;s{" "}
          {`${result.n_role_postings} postings`}. Same matching methodology as the program alignment scores, so these
          numbers are directly comparable to a program&apos;s headline score.
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
        <div>
          <h2 className="inline-flex items-center gap-1.5 text-base font-semibold">
            <CheckCircle2 className="h-4 w-4 text-score-strong" aria-hidden /> Covered skills
          </h2>
          <p className="text-xs text-muted">Role-demanded skills this program covers (★ = core skill).</p>
          <ul className="mt-3 space-y-1">
            {result.matched.slice(0, 25).map((s) => (
              <li key={s.skill} className="flex justify-between rounded-lg border border-border bg-surface px-3 py-1.5 text-sm">
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
          <h2 className="inline-flex items-center gap-1.5 text-base font-semibold">
            <AlertTriangle className="h-4 w-4 text-score-moderate" aria-hidden /> Missing core skills
          </h2>
          <p className="text-xs text-muted">High-demand skills for this role that the program doesn&apos;t cover.</p>
          <ul className="mt-3 space-y-1">
            {result.missing.map((s) => (
              <li key={s.skill} className="flex justify-between rounded-lg border border-border bg-surface px-3 py-1.5 text-sm">
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
  );
}

