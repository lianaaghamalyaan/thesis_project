"use client";

import { Suspense, useMemo } from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Bar, BarChart, CartesianGrid, Cell, LabelList, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { FileText, Search, Sparkles } from "lucide-react";
import { api, DocumentationLevel } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { MetricCard } from "@/components/MetricCard";
import { InfoTip } from "@/components/InfoTip";
import { DataFreshnessNote } from "@/components/DataFreshnessNote";
import { DocBadge, ErrorState, PageHeader, PageSkeleton, ScoreBar, TierLegend } from "@/components/ui";
import { formatDate, formatScore, scoreFill, uniAbbr } from "@/lib/format";
import { useApi } from "@/lib/useApi";

function OverviewPageInner() {
  const { currentUniversity, universityParam, isAllUniversities } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const degreeFilter = searchParams.get("degree") ?? "All";
  const setDegreeFilter = (value: string) => {
    const next = new URLSearchParams(searchParams.toString());
    if (value === "All") next.delete("degree");
    else next.set("degree", value);
    router.replace(`${pathname}${next.size ? `?${next}` : ""}`, { scroll: false });
  };

  const programsQ = useApi(() => api.programs(universityParam), [universityParam], !!currentUniversity);
  const gapsQ = useApi(() => api.gaps(universityParam), [universityParam], !!currentUniversity);
  const metaQ = useApi(() => api.runMetadata(), []);
  const docQualityQ = useApi(() => api.docQuality(universityParam), [universityParam], !!currentUniversity);

  const programs = programsQ.data;
  const gaps = gapsQ.data;
  const meta = metaQ.data;

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
  const scored = useMemo(
    () =>
      (programs ?? []).filter(
        (p) => p.weighted_core_coverage_pct !== null && (degreeFilter === "All" || p.degree === degreeFilter)
      ),
    [programs, degreeFilter]
  );
  const meanScore = scored.length
    ? scored.reduce((sum, p) => sum + (p.weighted_core_coverage_pct ?? 0), 0) / scored.length
    : null;
  const nGapSkills = useMemo(() => new Set((gaps ?? []).map((g) => g.gap_skill)).size, [gaps]);

  const chartData = useMemo(
    () =>
      [...scored]
        .sort((a, b) => (a.weighted_core_coverage_pct ?? 0) - (b.weighted_core_coverage_pct ?? 0))
        .map((p) => ({
          name: isAllUniversities
            ? `${p.program} (${p.degree}) · ${uniAbbr(p.university)}`
            : `${p.program} (${p.degree})`,
          score: p.weighted_core_coverage_pct ?? 0,
          href: `/programs/${encodeURIComponent(p.program)}/${encodeURIComponent(p.degree)}?u=${encodeURIComponent(p.university)}`,
        })),
    [scored, isAllUniversities]
  );

  const topGaps = useMemo(() => {
    const byFreq = new Map<string, number>();
    for (const g of gaps ?? []) {
      byFreq.set(g.gap_skill, (byFreq.get(g.gap_skill) ?? 0) + (g.job_frequency ?? 0));
    }
    return [...byFreq.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([skill, freq]) => ({ skill, freq }))
      .reverse();
  }, [gaps]);

  const strongest = useMemo(
    () => [...scored].sort((a, b) => (b.weighted_core_coverage_pct ?? 0) - (a.weighted_core_coverage_pct ?? 0)).slice(0, 3),
    [scored]
  );

  if (programsQ.error) return <ErrorState message={programsQ.error} onRetry={programsQ.retry} />;
  if (!programs) return <PageSkeleton />;

  return (
    <div>
      <PageHeader
        title="Overview"
        subtitle={
          <>
            A portfolio-level snapshot for{" "}
            <span className="font-semibold text-foreground">
              {isAllUniversities ? "all universities" : currentUniversity}
            </span>{" "}
            — how programs are doing overall. To look up one specific program, go to{" "}
            <Link href="/programs" className="font-medium text-primary">Programs</Link>.
          </>
        }
      />
      {meta && (
        <p className="mt-0.5 text-xs text-muted">
          {meta.curriculum_snapshot.n_programs} programs · {meta.curriculum_snapshot.n_courses?.toLocaleString()} courses
        </p>
      )}

      <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <MetricCard label="Programs" value={programs.length} />
        <MetricCard
          label={<>Average market alignment <InfoTip term="weighted_coverage" /></>}
          value={meanScore !== null ? formatScore(meanScore) : "—"}
        />
        <MetricCard label="Unique gap skills" value={nGapSkills} />
        <MetricCard
          label="Analysis last generated"
          value={meta ? formatDate(meta.created_at) : "—"}
          caption={meta ? `Run ID: ${meta.run_id}` : undefined}
        />
      </div>

      {strongest.length > 0 && (
        <div className="mt-6 rounded-xl border-l-4 border-accent bg-surface p-5 shadow-card ring-1 ring-border/60">
          <h2 className="inline-flex items-center gap-2 font-display text-lg font-bold text-primary-dark">
            <FileText className="h-4 w-4 text-accent" aria-hidden /> Executive summary
          </h2>
          <ul className="mt-2 space-y-1.5 text-[15px] leading-relaxed">
            <li>
              The strongest program {isAllUniversities ? "across universities" : "in this portfolio"} is{" "}
              <strong>{strongest[0].program} ({strongest[0].degree})</strong> at{" "}
              {formatScore(strongest[0].weighted_core_coverage_pct)} market alignment.
            </li>
            {topGaps.length > 0 && (
              <li>
                The most demanded skill currently missing from programs is{" "}
                <strong>{topGaps[topGaps.length - 1].skill}</strong>, asked for in{" "}
                {topGaps[topGaps.length - 1].freq} job postings.
              </li>
            )}
            {docQualityQ.data && docQualityQ.data.programs.some((prog) => prog.documentation_level !== "full") && (
              <li>
                {docQualityQ.data.programs.filter((prog) => prog.documentation_level !== "full").length} of{" "}
                {docQualityQ.data.programs.length} programs have limited published course descriptions — their scores
                are likely understated and improving documentation is the fastest win.
              </li>
            )}
          </ul>
        </div>
      )}

      <hr className="my-6 border-border" />

      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">
          Score distribution — {degreeFilter === "All" ? "all programs" : `${degreeFilter} programs`}
        </h2>
        <div className="inline-flex rounded-lg border border-border bg-surface p-0.5" role="tablist" aria-label="Degree filter">
          {degrees.map((d) => (
            <button
              key={d}
              role="tab"
              aria-selected={degreeFilter === d}
              onClick={() => setDegreeFilter(d)}
              className={`rounded-md px-3 py-1 text-xs font-medium ${
                degreeFilter === d ? "bg-primary text-white" : "text-muted hover:bg-surface-muted"
              }`}
            >
              {d === "All" ? "All degrees" : d}
            </button>
          ))}
        </div>
      </div>
      <p className="max-w-3xl text-xs leading-relaxed text-muted">
        Each bar is one program&apos;s own alignment score, from 0% to 100%. Bars are independent — they compare a
        program against its own relevant job market, not against each other, so they are not parts of a whole and
        will never add up to 100%.
      </p>
      <TierLegend className="mt-2" />
      <div className="mt-3" style={{ height: Math.max(320, chartData.length * 34) }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: 24, right: 40 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" domain={[0, 100]} ticks={[0, 20, 40, 60, 80, 100]} tickFormatter={(v) => `${v}%`} fontSize={12} />
            <YAxis type="category" dataKey="name" width={260} fontSize={11} interval={0} />
            <Tooltip formatter={(v) => `${Number(v).toFixed(1)}%`} />
            {meanScore !== null && (
              <ReferenceLine
                x={meanScore}
                stroke="var(--muted)"
                strokeDasharray="4 4"
                label={{ value: `mean ${Math.round(meanScore)}%`, position: "top", fontSize: 10, fill: "var(--muted)" }}
              />
            )}
            <Bar
              dataKey="score"
              radius={[0, 4, 4, 0]}
              cursor="pointer"
              onClick={(data) => {
                const href = (data as { payload?: { href?: string } }).payload?.href;
                if (href) router.push(href);
              }}
            >
              <LabelList dataKey="score" position="right" formatter={(v: React.ReactNode) => `${Math.round(Number(v))}%`} fontSize={11} />
              {chartData.map((d, i) => (
                <Cell key={i} fill={scoreFill(d.score)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-2 text-xs text-muted">
        <Link href="/programs" className="font-medium text-primary">Browse the full list</Link>{" "}to filter, search,
        and open any program&apos;s detail page.
      </p>

      <hr className="my-6 border-border" />

      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        <div>
          <h2 className="inline-flex items-center gap-2 text-lg font-semibold">
            <Sparkles className="h-4 w-4 text-primary" aria-hidden /> Strongest programs
          </h2>
          <ul className="mt-3 space-y-4">
            {strongest.map((p) => (
              <li key={`${p.university}-${p.program}-${p.degree}`}>
                <div className="text-sm font-medium">
                  {p.program} ({p.degree}){isAllUniversities ? ` · ${uniAbbr(p.university)}` : ""}
                  <DocBadge level={docLevelFor(p.university, p.program, p.degree)} />
                </div>
                <div className="mt-1 flex items-center justify-between gap-4">
                  <ScoreBar score={p.weighted_core_coverage_pct} width="w-40" />
                  <span className="truncate text-xs text-muted">{p.relevant_roles ?? ""}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h2 className="inline-flex items-center gap-2 text-lg font-semibold">
            <Search className="h-4 w-4 text-primary" aria-hidden /> Most common gap skills
          </h2>
          <p className="text-xs text-muted">Horizontal axis: number of job postings demanding the skill.</p>
          <div className="mt-3" style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topGaps} layout="vertical" margin={{ left: 8, right: 20 }}>
                <XAxis type="number" fontSize={11} label={{ value: "# postings", position: "insideBottomRight", offset: -4, fontSize: 10 }} />
                <YAxis type="category" dataKey="skill" width={130} fontSize={11} interval={0} />
                <Tooltip formatter={(v) => [`${v} postings`, "Demand"]} />
                <Bar dataKey="freq" fill="var(--primary)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <DataFreshnessNote meta={meta} />
    </div>
  );
}

export default function OverviewPage() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <OverviewPageInner />
    </Suspense>
  );
}
