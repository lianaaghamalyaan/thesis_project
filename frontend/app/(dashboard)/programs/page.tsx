"use client";

import { Suspense, useMemo, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { ArrowLeftRight, ExternalLink, LayoutGrid, Table2, X } from "lucide-react";
import { api, DocumentationLevel } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ScoreDisplay } from "@/components/ScoreBadge";
import { DocBadge, EmptyState, ErrorState, PageHeader, PageSkeleton, ScoreBar, TierLegend } from "@/components/ui";
import { rolesShort, scoreLabel } from "@/lib/format";
import { useApi } from "@/lib/useApi";

const SORT_OPTIONS = [
  { value: "score", label: "Highest score first" },
  { value: "name", label: "Name (A–Z)" },
  { value: "gaps", label: "Most gaps first" },
] as const;

function ProgramsPageInner() {
  const { currentUniversity, universityParam, isAllUniversities } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // All filters live in the URL so filtered views are shareable/bookmarkable.
  const degreeFilter = searchParams.get("degree") ?? "All";
  const roleFilter = searchParams.get("role") ?? "All";
  const docFilter = searchParams.get("doc") ?? "All";
  const search = searchParams.get("q") ?? "";
  const sort = searchParams.get("sort") ?? "score";
  const view = searchParams.get("view") ?? "cards";

  const setParam = (key: string, value: string, defaultValue = "All") => {
    const next = new URLSearchParams(searchParams.toString());
    if (value === defaultValue || value === "") next.delete(key);
    else next.set(key, value);
    router.replace(`${pathname}${next.size ? `?${next}` : ""}`, { scroll: false });
  };

  // Compare selection: up to 2 programs, keyed "program|degree|university".
  const [compareKeys, setCompareKeys] = useState<string[]>([]);
  const toggleCompare = (key: string) =>
    setCompareKeys((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : prev.length >= 2 ? [prev[1], key] : [...prev, key]
    );

  const programsQ = useApi(() => api.programs(universityParam), [universityParam], !!currentUniversity);
  const docQualityQ = useApi(() => api.docQuality(universityParam), [universityParam], !!currentUniversity);
  const programs = programsQ.data;

  const docLevelFor = (university: string, program: string, degree: string): DocumentationLevel | null => {
    const row = docQualityQ.data?.programs.find(
      (p) => p.university === university && p.program === program && p.degree === degree
    );
    return row ? row.documentation_level : null;
  };

  const degrees = useMemo(
    () => ["All", ...Array.from(new Set((programs ?? []).map((p) => p.degree))).sort()],
    [programs]
  );

  const roleGroups = useMemo(() => {
    const set = new Set<string>();
    for (const p of programs ?? []) {
      for (const r of (p.relevant_roles ?? "").split(",").map((s) => s.trim()).filter(Boolean)) set.add(r);
    }
    return ["All", ...Array.from(set).sort()];
  }, [programs]);

  const filtered = useMemo(() => {
    const rows = (programs ?? [])
      .filter((p) => degreeFilter === "All" || p.degree === degreeFilter)
      .filter((p) => roleFilter === "All" || (p.relevant_roles ?? "").split(",").map((s) => s.trim()).includes(roleFilter))
      .filter((p) => {
        if (docFilter === "All") return true;
        const level = docLevelFor(p.university, p.program, p.degree);
        return docFilter === "limited" ? level !== null && level !== "full" : level === "full";
      })
      .filter(
        (p) =>
          p.program.toLowerCase().includes(search.toLowerCase()) ||
          p.university.toLowerCase().includes(search.toLowerCase())
      );
    switch (sort) {
      case "name":
        return rows.sort((a, b) => a.program.localeCompare(b.program));
      case "gaps":
        return rows.sort((a, b) => (b.core_n_gap ?? -1) - (a.core_n_gap ?? -1));
      default:
        return rows.sort((a, b) => (b.weighted_core_coverage_pct ?? -1) - (a.weighted_core_coverage_pct ?? -1));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [programs, degreeFilter, roleFilter, docFilter, search, sort, docQualityQ.data]);

  if (programsQ.error) return <ErrorState message={programsQ.error} onRetry={programsQ.retry} />;
  if (!programs) return <PageSkeleton />;

  const detailHref = (p: (typeof programs)[number]) =>
    `/programs/${encodeURIComponent(p.program)}/${encodeURIComponent(p.degree)}?u=${encodeURIComponent(p.university)}`;
  const compareKey = (p: (typeof programs)[number]) => `${p.program}|${p.degree}|${p.university}`;
  const compareHref =
    compareKeys.length === 2
      ? `/programs/compare?a=${encodeURIComponent(compareKeys[0])}&b=${encodeURIComponent(compareKeys[1])}`
      : null;

  return (
    <div>
      <PageHeader
        title="Programs"
        subtitle={
          <>
            The full, searchable catalog of programs. {isAllUniversities ? "Across every university, " : ""}Filter or
            search below, then open a program to see its full strengths/gaps breakdown. For a portfolio-level summary
            instead, see <Link href="/" className="font-medium text-primary">Overview</Link>.
          </>
        }
      />

      {/* Degree segmented control — the primary comparison cut (bachelor vs master). */}
      <div className="mt-5 inline-flex rounded-lg border border-border bg-surface p-0.5" role="tablist" aria-label="Degree filter">
        {degrees.map((d) => (
          <button
            key={d}
            role="tab"
            aria-selected={degreeFilter === d}
            onClick={() => setParam("degree", d)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium ${
              degreeFilter === d ? "bg-primary text-white" : "text-muted hover:bg-surface-muted"
            }`}
          >
            {d === "All" ? "All degrees" : d}
          </button>
        ))}
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-3">
        <select
          value={roleFilter}
          onChange={(e) => setParam("role", e.target.value)}
          aria-label="Filter by role group"
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm"
        >
          {roleGroups.map((r) => (
            <option key={r} value={r}>
              {r === "All" ? "All role groups" : r}
            </option>
          ))}
        </select>
        <select
          value={docFilter}
          onChange={(e) => setParam("doc", e.target.value)}
          aria-label="Filter by documentation level"
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm"
        >
          <option value="All">Any documentation</option>
          <option value="full">Fully documented</option>
          <option value="limited">Limited documentation</option>
        </select>
        <select
          value={sort}
          onChange={(e) => setParam("sort", e.target.value, "score")}
          aria-label="Sort programs"
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm"
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <input
          type="search"
          placeholder={isAllUniversities ? "Search by program or university…" : "e.g. Data Science, Information Security…"}
          value={search}
          onChange={(e) => setParam("q", e.target.value, "")}
          aria-label="Search programs"
          className="min-w-64 flex-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm"
        />
        <button
          onClick={() => setParam("view", view === "cards" ? "table" : "cards", "cards")}
          aria-label={view === "cards" ? "Switch to table view" : "Switch to card view"}
          className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-surface px-3 py-2 text-sm font-medium hover:bg-surface-muted"
        >
          {view === "cards" ? <Table2 className="h-4 w-4" aria-hidden /> : <LayoutGrid className="h-4 w-4" aria-hidden />}
          {view === "cards" ? "Table" : "Cards"}
        </button>
      </div>

      <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs text-muted">Showing {filtered.length} of {programs.length} programs</p>
        <TierLegend />
      </div>

      {filtered.length === 0 && (
        <EmptyState
          title="No programs match these filters"
          hint="Try clearing the search or switching the degree filter."
          action={
            <button onClick={() => router.replace(pathname)} className="rounded-lg border border-border px-3 py-1.5 text-sm font-medium hover:bg-surface-muted">
              Clear all filters
            </button>
          }
        />
      )}

      {view === "table" && filtered.length > 0 && (
        <div className="mt-3 overflow-x-auto rounded-xl bg-surface shadow-card ring-1 ring-border/60">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted">
                <th className="px-4 py-2.5 font-medium">Program</th>
                <th className="px-4 py-2.5 font-medium">Degree</th>
                {isAllUniversities && <th className="px-4 py-2.5 font-medium">University</th>}
                <th className="px-4 py-2.5 font-medium">Role groups</th>
                <th className="px-4 py-2.5 font-medium">Alignment</th>
                <th className="px-4 py-2.5 font-medium">Tier</th>
                <th className="px-4 py-2.5 font-medium">Core gaps</th>
                <th className="px-4 py-2.5" />
              </tr>
            </thead>
            <tbody>
              {filtered.map((p) => (
                <tr key={`${p.university}-${p.program}-${p.degree}`} className="border-b border-border/60 last:border-0 hover:bg-surface-muted/60">
                  <td className="px-4 py-2.5 font-medium">
                    <label className="inline-flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={compareKeys.includes(compareKey(p))}
                        onChange={() => toggleCompare(compareKey(p))}
                        aria-label={`Select ${p.program} (${p.degree}) for comparison`}
                        className="h-3.5 w-3.5 accent-[var(--primary)]"
                      />
                      {p.program}
                    </label>
                    <DocBadge level={docLevelFor(p.university, p.program, p.degree)} />
                  </td>
                  <td className="px-4 py-2.5 text-muted">{p.degree}</td>
                  {isAllUniversities && <td className="px-4 py-2.5 text-muted">{p.university}</td>}
                  <td className="px-4 py-2.5 text-muted">{rolesShort(p.relevant_roles)}</td>
                  <td className="px-4 py-2.5"><ScoreBar score={p.weighted_core_coverage_pct} /></td>
                  <td className="px-4 py-2.5 text-xs text-muted">{scoreLabel(p.weighted_core_coverage_pct)}</td>
                  <td className="px-4 py-2.5 tabular-nums text-muted">{p.core_n_gap ?? "—"}</td>
                  <td className="px-4 py-2.5 text-right">
                    <Link href={detailHref(p)} className="font-medium text-primary hover:underline">
                      View →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {compareKeys.length > 0 && (
        <div className="sticky bottom-4 z-10 mt-4 flex items-center justify-between gap-4 rounded-xl bg-primary-dark px-4 py-3 text-sm text-white shadow-lg">
          <span>
            {compareKeys.length === 1
              ? `1 program selected — pick one more to compare`
              : `2 programs selected`}
          </span>
          <span className="flex items-center gap-2">
            {compareHref && (
              <Link
                href={compareHref}
                className="inline-flex items-center gap-1.5 rounded-lg bg-white px-3 py-1.5 font-medium text-primary-dark hover:bg-white/90"
              >
                <ArrowLeftRight className="h-4 w-4" aria-hidden /> Compare side by side
              </Link>
            )}
            <button
              onClick={() => setCompareKeys([])}
              aria-label="Clear comparison selection"
              className="rounded-lg border border-white/30 p-1.5 hover:bg-white/10"
            >
              <X className="h-4 w-4" aria-hidden />
            </button>
          </span>
        </div>
      )}

      {view === "cards" && (
        <ul className="mt-3 space-y-3">
          {filtered.map((p) => (
            <li
              key={`${p.university}-${p.program}-${p.degree}`}
              className="flex items-center justify-between rounded-xl bg-surface p-4 shadow-card ring-1 ring-border/60"
            >
              <div>
                <div className="font-semibold">
                  <label className="inline-flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={compareKeys.includes(compareKey(p))}
                      onChange={() => toggleCompare(compareKey(p))}
                      aria-label={`Select ${p.program} (${p.degree}) for comparison`}
                      className="h-3.5 w-3.5 accent-[var(--primary)]"
                    />
                    {p.program}
                  </label>
                  <DocBadge level={docLevelFor(p.university, p.program, p.degree)} />
                </div>
                <div className="text-xs text-muted">
                  {p.degree} · {rolesShort(p.relevant_roles)}
                  {isAllUniversities ? ` · ${p.university}` : ""}
                  {p.source_url && (
                    <>
                      {" · "}
                      <a
                        href={p.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-0.5 font-medium text-primary hover:underline"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <ExternalLink className="h-3 w-3" aria-hidden /> Curriculum on university site
                      </a>
                    </>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-6">
                <ScoreDisplay score={p.weighted_core_coverage_pct} size="md" />
                <Link
                  href={detailHref(p)}
                  className="rounded-lg border border-border px-3 py-1.5 text-sm font-medium hover:bg-surface-muted"
                >
                  View →
                </Link>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function ProgramsPage() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <ProgramsPageInner />
    </Suspense>
  );
}
