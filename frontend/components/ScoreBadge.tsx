import { formatScore, scoreColor, scoreLabel } from "@/lib/format";

export function ScoreBadge({ score }: { score: number | null | undefined }) {
  return (
    <span
      className="inline-block rounded-full px-3 py-0.5 text-xs font-semibold text-white"
      style={{ backgroundColor: scoreColor(score) }}
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
