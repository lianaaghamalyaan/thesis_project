"use client";

import { useEffect, useState } from "react";
import { api, DocQualityResponse, RunMetadata } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/MetricCard";
import { InfoTip } from "@/components/InfoTip";
import { formatExperiment } from "@/lib/experiments";
import { DOC_LEVEL_ICONS, DOC_LEVEL_LABELS, DOC_LEVEL_SHORT_LABELS, formatDate } from "@/lib/format";

function docStatus(score: number): string {
  if (score < 0.25) return "⚠️";
  if (score < 0.4) return "🟡";
  return "✅";
}

export default function AdminPage() {
  const { currentUniversity, universityParam, isAllUniversities } = useAuth();
  const [meta, setMeta] = useState<RunMetadata | null>(null);
  const [docQuality, setDocQuality] = useState<DocQualityResponse | null>(null);

  useEffect(() => {
    api.runMetadata().then(setMeta);
  }, []);

  useEffect(() => {
    if (!currentUniversity || isAllUniversities) {
      setDocQuality(null);
      return;
    }
    api.docQuality(universityParam).then(setDocQuality);
  }, [currentUniversity, universityParam, isAllUniversities]);

  return (
    <div>
      <h1 className="text-3xl font-bold text-primary-dark">Data & Admin</h1>
      <p className="mt-1 text-sm text-muted">
        What data this dashboard is based on, when it was collected, and when the analysis was last computed from
        it.
      </p>

      {meta && (
        <>
          <p className="mt-4 rounded-lg bg-surface px-4 py-3 text-sm">
            🧮 <strong>Analysis generated on {formatDate(meta.created_at)}</strong> — this is when the scores you see
            throughout the dashboard were computed. It is separate from the two data-collection dates below; the
            underlying data can be older than the analysis date if nothing has changed since collection.
          </p>

          <h2 className="mt-6 text-lg font-semibold">📅 What data was used, and when it was collected</h2>
          <p className="text-xs text-muted">
            Two independent datasets feed every score: the courses each university publishes, and job postings from
            the Armenian IT market. Both are one-time snapshots, refreshed manually — see the note at the bottom of
            this section.
          </p>
          <div className="mt-2 grid grid-cols-2 gap-6 text-sm">
            <Card>
              <div className="font-semibold">💼 Job market data</div>
              <p className="mt-1 text-muted">
                Status: 🟡 Static snapshot (not live)
                <br />
                Job postings data collected on: <strong>{formatDate(meta.job_snapshot.collected_at)}</strong>
                <br />
                IT postings analyzed: <strong>{meta.job_snapshot.n_it_postings?.toLocaleString()}</strong>
                <br />
                From sources: <strong>{meta.job_snapshot.n_sources}</strong> Armenian job boards / company career
                pages
              </p>
            </Card>
            <Card>
              <div className="font-semibold">🎓 Curriculum data</div>
              <p className="mt-1 text-muted">
                Status: 🟡 Static snapshot (not live)
                <br />
                Course catalog data collected on: <strong>{formatDate(meta.curriculum_snapshot.collected_at)}</strong>
                <br />
                Courses analyzed: <strong>{meta.curriculum_snapshot.n_courses?.toLocaleString()}</strong>
                <br />
                Across <strong>{meta.curriculum_snapshot.n_programs}</strong> programs at{" "}
                <strong>{meta.curriculum_snapshot.n_universities}</strong> universities
              </p>
            </Card>
          </div>

          <h2 className="mt-6 text-lg font-semibold">⚙️ How the analysis was computed</h2>
          <Card className="mt-2 text-sm">
            <p>
              <strong>Method used:</strong> {formatExperiment(meta.experiment)} <InfoTip term="experiment" />
              <br />
              <strong>Run identifier:</strong> <span className="font-mono text-xs">{meta.run_id}</span> (for citing
              this exact analysis run)
              <br />
              <strong>Notes:</strong> {meta.notes ?? "—"}
            </p>
          </Card>
        </>
      )}

      {isAllUniversities && (
        <p className="mt-6 rounded-lg bg-surface px-4 py-3 text-sm text-muted">
          Documentation quality is reported per university — select a specific university in the banner above to
          see it.
        </p>
      )}

      {docQuality && (
        <>
          <h2 className="mt-6 text-lg font-semibold">
            📝 Documentation quality by program <InfoTip term="doc_score" />
          </h2>
          <p className="text-xs text-muted">
            Programs with low documentation quality may show lower alignment scores because there wasn&apos;t much
            published course detail to analyze — not necessarily because the curriculum itself is weak. &ldquo;Data
            level&rdquo; below shows exactly what was published per program: how many courses have no description at
            all, how many were filled in with an AI-generated description because none existed, how many have only a
            short/thin one, and how many have a full published description. See{" "}
            <a href="/methodology#fairness" className="font-medium text-primary">Methodology</a> for more.
          </p>
          <table className="mt-3 w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs text-muted">
                <th className="py-2">Program</th>
                <th>Degree</th>
                <th>Courses</th>
                <th>Data level</th>
                <th>Doc. quality</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {docQuality.programs.map((p) => (
                <tr key={`${p.program}-${p.degree}`} className="border-b border-border/60">
                  <td className="py-1.5">{p.program}</td>
                  <td>{p.degree}</td>
                  <td>{p.n_courses}</td>
                  <td>
                    <span title={DOC_LEVEL_LABELS[p.documentation_level]} className="cursor-help">
                      {DOC_LEVEL_ICONS[p.documentation_level]} {DOC_LEVEL_SHORT_LABELS[p.documentation_level]}
                    </span>
                    <div className="text-[10px] text-muted">
                      {p.n_missing > 0 && <>{p.n_missing} no description</>}
                      {p.n_missing > 0 && (p.n_ai_generated > 0 || p.n_short > 0) && " · "}
                      {p.n_ai_generated > 0 && <>{p.n_ai_generated} AI-generated</>}
                      {p.n_ai_generated > 0 && p.n_short > 0 && " · "}
                      {p.n_short > 0 && <>{p.n_short} very short</>}
                    </div>
                  </td>
                  <td>{(p.doc_score * 100).toFixed(0)}%</td>
                  <td>{docStatus(p.doc_score)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="mt-2 text-xs text-muted">
            Data level: ⛔ No published data · 🟠 Minimal · 🟡 Partial · ✅ Full. Doc. quality/Status is the
            skill-extraction confidence score described above. ✅ Good (≥40%) · 🟡 Mixed (25–40%) · ⚠️ Weak
            (&lt;25%)
          </p>

          {docQuality.missing_descriptions.length > 0 && (
            <>
              <h2 className="mt-6 text-lg font-semibold">⚠️ Courses with missing or short descriptions</h2>
              <p className="text-xs text-muted">
                {docQuality.missing_descriptions.length} courses cannot be analyzed for skill alignment.
              </p>
              <ul className="mt-3 space-y-1">
                {docQuality.missing_descriptions.slice(0, 30).map((c, i) => (
                  <li key={i} className="rounded-lg border border-border px-3 py-1.5 text-sm">
                    {c.course_name} <span className="text-xs text-muted">({c.program_name}, {c.degree_level})</span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </>
      )}
    </div>
  );
}
