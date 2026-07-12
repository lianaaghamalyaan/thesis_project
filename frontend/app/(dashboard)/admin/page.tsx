"use client";

import { useEffect, useState } from "react";
import { api, DocQualityResponse, RunMetadata } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/MetricCard";

function docStatus(score: number): string {
  if (score < 0.25) return "⚠️";
  if (score < 0.4) return "🟡";
  return "✅";
}

export default function AdminPage() {
  const { currentUniversity } = useAuth();
  const [meta, setMeta] = useState<RunMetadata | null>(null);
  const [docQuality, setDocQuality] = useState<DocQualityResponse | null>(null);

  useEffect(() => {
    api.runMetadata().then(setMeta);
  }, []);

  useEffect(() => {
    if (currentUniversity) api.docQuality(currentUniversity).then(setDocQuality);
  }, [currentUniversity]);

  return (
    <div>
      <h1 className="text-3xl font-bold text-primary-dark">Data & Admin</h1>
      <p className="mt-1 text-sm text-muted">Data freshness, pipeline status, and documentation quality.</p>

      {meta && (
        <>
          <h2 className="mt-6 text-lg font-semibold">📅 Data freshness</h2>
          <Card className="mt-2">
            <div className="grid grid-cols-2 gap-6 text-sm">
              <div>
                <div className="font-semibold">Job market data</div>
                <p className="mt-1 text-muted">
                  Status: 🟡 Static snapshot
                  <br />
                  Last collected: <strong>{meta.job_snapshot.collected_at}</strong>
                  <br />
                  IT postings: <strong>{meta.job_snapshot.n_it_postings?.toLocaleString()}</strong>
                  <br />
                  Sources: <strong>{meta.job_snapshot.n_sources}</strong>
                </p>
              </div>
              <div>
                <div className="font-semibold">Curriculum data</div>
                <p className="mt-1 text-muted">
                  Status: 🟡 Static snapshot
                  <br />
                  Last collected: <strong>{meta.curriculum_snapshot.collected_at}</strong>
                  <br />
                  Courses: <strong>{meta.curriculum_snapshot.n_courses?.toLocaleString()}</strong>
                  <br />
                  Programs: <strong>{meta.curriculum_snapshot.n_programs}</strong>
                </p>
              </div>
            </div>
          </Card>

          <h2 className="mt-6 text-lg font-semibold">⚙️ Analysis pipeline</h2>
          <Card className="mt-2 text-sm">
            <p>
              <strong>Run ID:</strong> {meta.run_id}
              <br />
              <strong>Analysis date:</strong> {meta.created_at}
              <br />
              <strong>Experiment:</strong> {meta.experiment}
              <br />
              <strong>Notes:</strong> {meta.notes ?? "—"}
            </p>
          </Card>
        </>
      )}

      {docQuality && (
        <>
          <h2 className="mt-6 text-lg font-semibold">📝 Documentation quality by program</h2>
          <p className="text-xs text-muted">
            Programs with low documentation quality may show lower alignment scores due to incomplete descriptions.
          </p>
          <table className="mt-3 w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs text-muted">
                <th className="py-2">Program</th>
                <th>Degree</th>
                <th>Courses</th>
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
                  <td>{(p.doc_score * 100).toFixed(0)}%</td>
                  <td>{docStatus(p.doc_score)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="mt-2 text-xs text-muted">✅ Good (≥40%) · 🟡 Mixed (25–40%) · ⚠️ Weak (&lt;25%)</p>

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
