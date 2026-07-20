import { RunMetadata } from "@/lib/api";
import { formatDate, formatJobDateRange } from "@/lib/format";

export function DataFreshnessNote({ meta }: { meta: RunMetadata | null }) {
  if (!meta) return null;
  const unknown = meta.job_snapshot.n_unknown_date ?? 0;
  return (
    <p className="mt-6 rounded-lg bg-surface px-4 py-3 text-xs text-muted">
      📅 Curriculum data collected: <strong>{formatDate(meta.curriculum_snapshot.collected_at)}</strong> · Job
      postings collected:{" "}
      <strong>{formatJobDateRange(meta.job_snapshot.earliest_at, meta.job_snapshot.collected_at)}</strong>
      {unknown > 0 && ` (${unknown} active postings have no known collection date)`} · Analysis generated:{" "}
      <strong>{formatDate(meta.created_at)}</strong>. University curricula and the job market change over time — this
      dashboard can be refreshed and recalculated as new data becomes available.
    </p>
  );
}
