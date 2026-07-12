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
