import { RunMetadata } from "@/lib/api";
import { formatDate } from "@/lib/format";

export function DataFreshnessNote({ meta }: { meta: RunMetadata | null }) {
  if (!meta) return null;
  return (
    <p className="mt-6 rounded-lg bg-surface px-4 py-3 text-xs text-muted">
      📅 Curriculum data collected: <strong>{formatDate(meta.curriculum_snapshot.collected_at)}</strong> · Job
      market data collected: <strong>{formatDate(meta.job_snapshot.collected_at)}</strong> · Analysis generated:{" "}
      <strong>{formatDate(meta.created_at)}</strong>. University curricula and the job market change over time — this
      dashboard can be refreshed and recalculated as new data becomes available.
    </p>
  );
}
