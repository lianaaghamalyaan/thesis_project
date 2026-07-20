export function MetricCard({
  label,
  value,
  caption,
}: {
  label: React.ReactNode;
  value: React.ReactNode;
  caption?: string;
}) {
  return (
    <div className="rounded-xl bg-surface px-4 py-3 shadow-card ring-1 ring-border/60">
      <div className="flex items-center gap-1 text-xs font-medium text-muted">{label}</div>
      <div className="font-display mt-1 text-2xl font-bold text-primary-dark">{value}</div>
      {caption && <div className="mt-1 text-xs text-muted">{caption}</div>}
    </div>
  );
}

export function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={`rounded-xl bg-surface p-5 shadow-card ring-1 ring-border/60 ${className}`}>{children}</div>;
}
