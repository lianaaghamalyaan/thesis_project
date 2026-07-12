"use client";

import { useEffect, useState } from "react";
import { api, RunMetadata } from "@/lib/api";
import { Card, MetricCard } from "@/components/MetricCard";

export default function MethodologyPage() {
  const [meta, setMeta] = useState<RunMetadata | null>(null);

  useEffect(() => {
    api.runMetadata().then(setMeta);
  }, []);

  return (
    <div className="max-w-3xl">
      <h1 className="text-3xl font-bold text-primary-dark">📐 Methodology</h1>
      <p className="mt-1 text-sm text-muted">
        How alignment scores are computed, what the numbers mean, and where the underlying data comes from.
      </p>

      <h2 className="mt-6 text-lg font-semibold">What the score measures</h2>
      <Card className="mt-2">
        <p className="text-sm">
          <strong>Core role-aware coverage</strong> (the headline number shown throughout the dashboard) = the
          percentage of skills commonly required in job postings for roles relevant to a program that the program's
          courses demonstrably cover.
        </p>
        <table className="mt-3 w-full text-sm">
          <thead>
            <tr className="text-left text-muted">
              <th className="pb-1 pr-4">Score</th>
              <th className="pb-1">Meaning</th>
            </tr>
          </thead>
          <tbody>
            <tr><td className="pr-4 py-0.5">50%+</td><td><strong>Strong</strong> — covers over half the role-relevant market skills</td></tr>
            <tr><td className="pr-4 py-0.5">35–50%</td><td><strong>Good</strong> — solid coverage with targeted gaps</td></tr>
            <tr><td className="pr-4 py-0.5">25–35%</td><td><strong>Moderate</strong> — clear opportunities to strengthen alignment</td></tr>
            <tr><td className="pr-4 py-0.5">Below 25%</td><td><strong>Developing</strong> — significant gaps or documentation issues likely</td></tr>
          </tbody>
        </table>
        <p className="mt-3 text-sm text-muted">
          A lower score does not mean a program is poor — job postings routinely wishlist skills far beyond what any
          single degree could reasonably teach. The score reflects what is documented in course descriptions.
        </p>
      </Card>

      <h2 className="mt-6 text-lg font-semibold">Pipeline, step by step</h2>
      <Card className="mt-2">
        <ol className="list-decimal space-y-2 pl-5 text-sm">
          <li><strong>Skill extraction.</strong> An LLM extracts a normalized list of skill phrases from each course description and each job posting independently.</li>
          <li><strong>Skill consolidation.</strong> All extracted phrases (course-side and job-side together) are embedded and greedily clustered at cosine similarity ≥ 0.85; the most frequent phrase per cluster becomes canonical.</li>
          <li><strong>Matching.</strong> Bidirectional cosine similarity ≥ 0.65 between a program's and a job market's consolidated skills, with a hand-curated blocklist (e.g. React vs. Angular) and allowlist (e.g. Python → NumPy/Pandas).</li>
          <li><strong>Role scoping.</strong> Each program is scored against its relevant role group(s)' postings only, not the full IT market.</li>
          <li><strong>Core skill filtering.</strong> A market skill counts as core if it appears in at least 5% of that role's postings.</li>
          <li><strong>Weighting.</strong> The weighted core coverage metric weights each core skill by posting frequency rather than counting all core skills equally.</li>
        </ol>
      </Card>

      <h2 className="mt-6 text-lg font-semibold">Documentation gaps vs. curriculum gaps</h2>
      <Card className="mt-2 text-sm">
        <p>🔴 <strong>Curriculum gap</strong> — the skill is genuinely not taught.</p>
        <p className="mt-1">🟡 <strong>Documentation gap</strong> — the skill is likely taught but not explicitly described.</p>
        <p className="mt-1">⚪ <strong>Uncertain</strong> — not enough signal either way.</p>
      </Card>

      {meta && (
        <>
          <h2 className="mt-6 text-lg font-semibold">Reproducibility & data snapshot</h2>
          <div className="mt-2 grid grid-cols-3 gap-4">
            <MetricCard label="Job postings" value={meta.job_snapshot.n_it_postings ?? "—"} caption={`Collected: ${meta.job_snapshot.collected_at ?? "—"}`} />
            <MetricCard label="Programs" value={meta.curriculum_snapshot.n_programs ?? "—"} caption={`Courses: ${meta.curriculum_snapshot.n_courses ?? "—"}`} />
            <MetricCard label="Universities" value={meta.curriculum_snapshot.n_universities ?? "—"} caption={`Run: ${meta.run_id}`} />
          </div>
        </>
      )}
    </div>
  );
}
