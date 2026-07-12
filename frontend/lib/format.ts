export function scoreColor(score: number | null | undefined): string {
  if (score === null || score === undefined || Number.isNaN(score)) return "var(--score-none)";
  if (score >= 50) return "var(--score-strong)";
  if (score >= 35) return "var(--score-good)";
  if (score >= 25) return "var(--score-moderate)";
  return "var(--score-developing)";
}

export function scoreLabel(score: number | null | undefined): string {
  if (score === null || score === undefined || Number.isNaN(score)) return "No data";
  if (score >= 50) return "Strong";
  if (score >= 35) return "Good";
  if (score >= 25) return "Moderate";
  return "Developing";
}

export function formatScore(score: number | null | undefined): string {
  if (score === null || score === undefined || Number.isNaN(score)) return "—";
  return `${score.toFixed(1)}%`;
}

export function rolesDisplay(relevantRoles: string | null | undefined): string {
  if (!relevantRoles || ["unmapped", "nan", ""].includes(relevantRoles)) return "general IT";
  const parts = relevantRoles.split(",").map((r) => r.trim());
  if (parts.length > 3) return `${parts.slice(0, 3).join(", ")} and ${parts.length - 3} more role groups`;
  return parts.length === 2 ? parts.join(" and ") : parts.join(", ");
}

export function rolesShort(relevantRoles: string | null | undefined): string {
  if (!relevantRoles || ["unmapped", "nan", ""].includes(relevantRoles)) return "General IT";
  const parts = relevantRoles.split(",").map((r) => r.trim());
  if (parts.length > 2) return `${parts[0]} +${parts.length - 1}`;
  return parts.join(" / ");
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "unknown date";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
}

export function uniAbbr(name: string): string {
  const skip = new Set(["of", "the", "in", "and", "en", "de"]);
  const parts = name.split(/[\s-]+/).filter((w) => w && !skip.has(w.toLowerCase()));
  if (parts.length === 1) return parts[0].slice(0, 4).toUpperCase();
  return parts.map((w) => w[0]).join("").toUpperCase();
}

import type { DocumentationLevel } from "./api";

export const DOC_LEVEL_LABELS: Record<DocumentationLevel, string> = {
  no_published_data: "No published course data — analysis relies on AI-generated descriptions",
  minimal: "Minimal published data — mostly missing or AI-generated descriptions",
  partial: "Partial published data — some courses missing or thin descriptions",
  full: "Full course descriptions published",
};

export const DOC_LEVEL_SHORT_LABELS: Record<DocumentationLevel, string> = {
  no_published_data: "No published data",
  minimal: "Minimal data",
  partial: "Partial data",
  full: "Full data",
};

export const DOC_LEVEL_ICONS: Record<DocumentationLevel, string> = {
  no_published_data: "⛔",
  minimal: "🟠",
  partial: "🟡",
  full: "✅",
};

export const GAP_TYPE_ICONS: Record<string, string> = {
  curriculum_gap: "🔴",
  documentation_gap: "🟡",
  uncertain: "⚪",
};

export const GAP_TYPE_LABELS: Record<string, string> = {
  curriculum_gap: "Likely curriculum gap",
  documentation_gap: "Possible documentation gap",
  uncertain: "Unclear",
};
