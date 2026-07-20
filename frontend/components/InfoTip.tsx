import { GLOSSARY } from "@/lib/glossary";

// Built from <span>/<button> (phrasing content) rather than <details>, since
// InfoTip is used inline inside <p> tags throughout the dashboard and
// <details> is block content — nesting it in a <p> causes a React hydration
// error ("<summary> cannot be a descendant of <p>"). Shown on hover or
// keyboard focus via group-hover/group-focus-within, no JS state needed.
function TipBubble({ text, href, className = "" }: { text: string; href?: string; className?: string }) {
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
        {text}
        {href && (
          <a href={href} className="pointer-events-auto mt-1.5 block font-medium text-primary">
            Learn more →
          </a>
        )}
      </span>
    </span>
  );
}

export function InfoTip({ term, className = "" }: { term: keyof typeof GLOSSARY; className?: string }) {
  const entry = GLOSSARY[term];
  if (!entry) return null;
  return <TipBubble text={entry.text} href={entry.href} className={className} />;
}

// Same hover/focus tooltip as InfoTip, but for arbitrary text instead of a
// fixed glossary term — used for per-skill "what is this?" context
// (server/api/routes/job_skills.py's /skills/info), which is dynamic data,
// not a static methodology term.
export function TextTip({ text, className = "" }: { text: string; className?: string }) {
  return <TipBubble text={text} className={className} />;
}
