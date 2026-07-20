"use client";

import { AlertTriangle, RotateCw } from "lucide-react";
import { scoreColor, scoreFill, scoreLabel } from "@/lib/format";
import type { DocumentationLevel } from "@/lib/api";
import { DOC_LEVEL_LABELS, DOC_LEVEL_SHORT_LABELS } from "@/lib/format";

/** Serif page title over a short gold rule + optional subtitle — the
 *  standard "policy brief" page opener. */
export function PageHeader({ title, subtitle }: { title: React.ReactNode; subtitle?: React.ReactNode }) {
  return (
    <div>
      <div className="mb-3 h-1 w-12 rounded-full bg-accent" aria-hidden />
      <h1 className="font-display text-[2.1rem] font-bold leading-tight text-primary-dark">{title}</h1>
      {subtitle && <p className="mt-2 max-w-3xl text-[15px] leading-relaxed text-muted">{subtitle}</p>}
    </div>
  );
}

/** Thin inline score bar + number, for scannable ranking in lists/tables. */
export function ScoreBar({
  score,
  showLabel = false,
  width = "w-28",
}: {
  score: number | null | undefined;
  showLabel?: boolean;
  width?: string;
}) {
  const value = score === null || score === undefined || Number.isNaN(score) ? null : score;
  return (
    <span className="inline-flex items-center gap-2">
      <span className={`h-1.5 ${width} overflow-hidden rounded-full bg-surface-muted`} aria-hidden>
        <span
          className="block h-full rounded-full"
          style={{ width: `${Math.min(value ?? 0, 100)}%`, backgroundColor: scoreFill(value) }}
        />
      </span>
      <span className="text-sm font-semibold tabular-nums" style={{ color: scoreColor(value) }}>
        {value === null ? "—" : `${Math.round(value)}%`}
      </span>
      {showLabel && <span className="text-xs text-muted">{scoreLabel(value)}</span>}
    </span>
  );
}

const DOC_LEVEL_COLORS: Record<DocumentationLevel, string> = {
  no_published_data: "bg-red-50 text-red-700 ring-red-200",
  minimal: "bg-orange-50 text-orange-700 ring-orange-200",
  partial: "bg-amber-50 text-amber-700 ring-amber-200",
  full: "bg-green-50 text-green-700 ring-green-200",
};

/** Documentation-quality pill; hidden for fully documented programs by default. */
export function DocBadge({
  level,
  showFull = false,
}: {
  level: DocumentationLevel | null | undefined;
  showFull?: boolean;
}) {
  if (!level || (level === "full" && !showFull)) return null;
  return (
    <span
      title={DOC_LEVEL_LABELS[level]}
      className={`ml-2 inline-block cursor-help rounded-full px-2 py-0.5 align-middle text-[10px] font-medium ring-1 ${DOC_LEVEL_COLORS[level]}`}
    >
      {DOC_LEVEL_SHORT_LABELS[level]}
    </span>
  );
}

const TIERS = [
  { label: "Strong", range: "≥ 50%", color: "var(--score-strong)" },
  { label: "Good", range: "35–50%", color: "var(--score-good)" },
  { label: "Moderate", range: "25–35%", color: "var(--score-moderate)" },
  { label: "Developing", range: "< 25%", color: "var(--score-developing)" },
];

/** Explains what the score colors mean — shown wherever colored scores appear. */
export function TierLegend({ className = "" }: { className?: string }) {
  return (
    <div className={`flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted ${className}`}>
      {TIERS.map((t) => (
        <span key={t.label} className="inline-flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full" style={{ backgroundColor: t.color }} />
          {t.label} <span className="opacity-70">{t.range}</span>
        </span>
      ))}
    </div>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`skeleton ${className}`} aria-hidden />;
}

/** Standard page-level loading state: header + a few content blocks. */
export function PageSkeleton() {
  return (
    <div aria-busy="true" aria-label="Loading">
      <Skeleton className="h-9 w-64" />
      <Skeleton className="mt-3 h-4 w-96" />
      <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-20" />
        ))}
      </div>
      <Skeleton className="mt-6 h-64" />
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="mt-6 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
      <div>
        <p className="font-medium">Couldn&apos;t load this data</p>
        <p className="mt-0.5 text-red-700">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 inline-flex items-center gap-1.5 rounded-lg border border-red-300 bg-white px-3 py-1 text-xs font-medium hover:bg-red-100"
          >
            <RotateCw className="h-3 w-3" aria-hidden /> Try again
          </button>
        )}
      </div>
    </div>
  );
}

export function EmptyState({ title, hint, action }: { title: string; hint?: string; action?: React.ReactNode }) {
  return (
    <div className="mt-6 rounded-xl border border-dashed border-border bg-surface px-6 py-10 text-center">
      <p className="text-sm font-medium">{title}</p>
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}
