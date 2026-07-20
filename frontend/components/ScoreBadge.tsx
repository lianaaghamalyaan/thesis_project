import { formatScore, scoreColor, scoreLabel } from "@/lib/format";

/** Soft tinted tier chip — colored text on a light wash of the same hue,
 *  calmer than a solid pill (constructive framing, not traffic lights). */
export function ScoreBadge({ score }: { score: number | null | undefined }) {
  const color = scoreColor(score);
  return (
    <span
      className="inline-block rounded-full px-3 py-0.5 text-xs font-semibold ring-1"
      style={{
        color,
        backgroundColor: `color-mix(in srgb, ${color} 10%, white)`,
        borderColor: `color-mix(in srgb, ${color} 25%, white)`,
        // Tailwind ring-1 uses box-shadow; set its color via CSS var:
        ["--tw-ring-color" as string]: `color-mix(in srgb, ${color} 30%, white)`,
      }}
    >
      {scoreLabel(score)}
    </span>
  );
}

export function ScoreDisplay({ score, size = "lg" }: { score: number | null | undefined; size?: "lg" | "md" }) {
  const textSize = size === "lg" ? "text-4xl" : "text-2xl";
  return (
    <div className="text-center">
      <div className={`font-display ${textSize} font-bold`} style={{ color: scoreColor(score) }}>
        {formatScore(score)}
      </div>
      <ScoreBadge score={score} />
    </div>
  );
}
