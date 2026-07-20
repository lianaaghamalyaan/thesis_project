"use client";

import { formatScore, scoreColor, scoreFill, scoreLabel } from "@/lib/format";
import { ScoreBadge } from "@/components/ScoreBadge";

/**
 * Semicircular gauge for the headline program score — communicates "a measured
 * value on a 0–100 scale" better than a floating number. Ticks mark the tier
 * boundaries used by scoreColor/scoreLabel (25 / 35 / 50).
 */
export function ScoreGauge({ score }: { score: number | null | undefined }) {
  const value = score === null || score === undefined || Number.isNaN(score) ? null : Math.min(Math.max(score, 0), 100);
  const cx = 90;
  const cy = 84;
  const r = 70;

  const angleFor = (pct: number) => Math.PI * (1 - pct / 100); // 180°→0°
  const pointAt = (pct: number, radius: number) => ({
    x: cx + radius * Math.cos(angleFor(pct)),
    y: cy - radius * Math.sin(angleFor(pct)),
  });

  const arcPath = (fromPct: number, toPct: number, radius: number) => {
    const a = pointAt(fromPct, radius);
    const b = pointAt(toPct, radius);
    const largeArc = toPct - fromPct > 50 ? 1 : 0;
    return `M ${a.x} ${a.y} A ${radius} ${radius} 0 ${largeArc} 1 ${b.x} ${b.y}`;
  };

  return (
    <div className="flex flex-col items-center">
      <svg width={180} height={100} role="img" aria-label={value === null ? "No score available" : `Alignment score ${Math.round(value)} percent — ${scoreLabel(value)}`}>
        <path d={arcPath(0, 100, r)} fill="none" stroke="var(--surface-muted)" strokeWidth={11} strokeLinecap="round" />
        {value !== null && value > 0 && (
          <path d={arcPath(0, value, r)} fill="none" stroke={scoreFill(value)} strokeWidth={11} strokeLinecap="round" />
        )}
        {/* Tier-boundary ticks */}
        {[25, 35, 50].map((t) => {
          const inner = pointAt(t, r - 10);
          const outer = pointAt(t, r + 10);
          return <line key={t} x1={inner.x} y1={inner.y} x2={outer.x} y2={outer.y} stroke="var(--border)" strokeWidth={1.5} />;
        })}
        <text x={cx} y={cy - 8} textAnchor="middle" className="font-display" fontSize={30} fontWeight={700} fill={scoreColor(value)}>
          {formatScore(value)}
        </text>
      </svg>
      <ScoreBadge score={value} />
    </div>
  );
}
