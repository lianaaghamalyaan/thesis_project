import { GLOSSARY } from "@/lib/glossary";

// Built from <span>/<button> (phrasing content) rather than <details>, since
// InfoTip is used inline inside <p> tags throughout the dashboard and
// <details> is block content — nesting it in a <p> causes a React hydration
// error ("<summary> cannot be a descendant of <p>"). Shown on hover or
// keyboard focus via group-hover/group-focus-within, no JS state needed.
export function InfoTip({ term, className = "" }: { term: keyof typeof GLOSSARY; className?: string }) {
  const entry = GLOSSARY[term];
  if (!entry) return null;

  return (
    <span className={`group relative inline-block align-middle ${className}`}>
      <button
        type="button"
        className="inline-flex h-4 w-4 cursor-pointer items-center justify-center rounded-full bg-border text-[10px] font-bold leading-none text-muted hover:bg-primary hover:text-white focus:bg-primary focus:text-white focus:outline-none"
        aria-label="More information"
      >
        i
      </button>
      <span className="pointer-events-none absolute left-1/2 top-6 z-20 w-64 -translate-x-1/2 rounded-lg border border-border bg-white p-3 text-xs font-normal normal-case leading-snug text-foreground opacity-0 shadow-lg transition-opacity group-hover:pointer-events-auto group-hover:opacity-100 group-focus-within:pointer-events-auto group-focus-within:opacity-100">
        {entry.text}
        {entry.href && (
          <a href={entry.href} className="pointer-events-auto mt-1.5 block font-medium text-primary">
            Learn more →
          </a>
        )}
      </span>
    </span>
  );
}
