"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Bar, BarChart, CartesianGrid, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, DocQualityResponse, GapSkillRow, ProgramAlignment, RunMetadata } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { MetricCard } from "@/components/MetricCard";
import { InfoTip } from "@/components/InfoTip";
import { DataFreshnessNote } from "@/components/DataFreshnessNote";
import { formatDate, formatScore, scoreColor, uniAbbr } from "@/lib/format";

const LOW_DOC_THRESHOLD = 0.25;

export default function OverviewPage() {
  const { currentUniversity, universityParam, isAllUniversities } = useAuth();
  const [programs, setPrograms] = useState<ProgramAlignment[] | null>(null);
  const [gaps, setGaps] = useState<GapSkillRow[] | null>(null);
  const [meta, setMeta] = useState<RunMetadata | null>(null);
  const [docQuality, setDocQuality] = useState<DocQualityResponse | null>(null);

  useEffect(() => {
    if (!currentUniversity) return;
    setPrograms(null);
    api.programs(universityParam).then(setPrograms);
    api.gaps(universityParam).then(setGaps);
    api.runMetadata().then(setMeta);
  }, [currentUniversity, universityParam]);

  useEffect(() => {
    if (!currentUniversity || isAllUniversities) {
      setDocQuality(null);
      return;
    }
    api.docQuality(universityParam).then(setDocQuality);
  }, [currentUniversity, universityParam, isAllUniversities]);

  const docScoreFor = (program: string, degree: string): number | null => {
    const row = docQuality?.programs.find((p) => p.program === program && p.degree === degree);
    return row ? row.doc_score : null;
  };

  const scored = useMemo(
    () => (programs ?? []).filter((p) => p.core_role_coverage_pct !== null),
    [programs]
  );
  const meanScore = scored.length
    ? scored.reduce((sum, p) => sum + (p.core_role_coverage_pct ?? 0), 0) / scored.length
    : null;
  const nGapSkills = useMemo(() => new Set((gaps ?? []).map((g) => g.gap_skill)).size, [gaps]);

  const chartData = useMemo(
    () =>
      [...scored]
        .sort((a, b) => (a.core_role_coverage_pct ?? 0) - (b.core_role_coverage_pct ?? 0))
        .map((p) => ({
          name: isAllUniversities
            ? `${p.program} (${p.degree}) · ${uniAbbr(p.university)}`
            : `${p.program} (${p.degree})`,
          score: p.core_role_coverage_pct ?? 0,
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
    () => [...scored].sort((a, b) => (b.core_role_coverage_pct ?? 0) - (a.core_role_coverage_pct ?? 0)).slice(0, 3),
    [scored]
  );

  if (!programs) return <p className="text-muted">Loading…</p>;

  return (
    <div>
      <h1 className="text-3xl font-bold text-primary-dark">Overview</h1>
      <p className="mt-1 text-sm text-muted">
        A portfolio-level snapshot for{" "}
        <span className="font-semibold text-foreground">
          {isAllUniversities ? "all universities" : currentUniversity}
        </span>{" "}
        — how programs are doing overall. To look up one specific program, go to{" "}
        <Link href="/programs" className="font-medium text-primary">Programs</Link>.
      </p>
      {meta && (
        <p className="mt-0.5 text-xs text-muted">
          {meta.curriculum_snapshot.n_programs} programs · {meta.curriculum_snapshot.n_courses?.toLocaleString()} courses
        </p>
      )}

      <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <MetricCard label="Programs" value={programs.length} />
        <MetricCard
          label={<>Mean alignment score <InfoTip term="core_coverage" /></>}
          value={meanScore !== null ? formatScore(meanScore) : "—"}
        />
        <MetricCard label="Unique gap skills" value={nGapSkills} />
        <MetricCard
          label="Analysis last generated"
          value={meta ? formatDate(meta.created_at) : "—"}
          caption={meta ? `Run ID: ${meta.run_id}` : undefined}
        />
      </div>

      <hr className="my-6 border-border" />

      <h2 className="text-lg font-semibold">Score distribution — all programs</h2>
      <p className="text-xs text-muted">
        Each bar is one program&apos;s own alignment score, from 0% to 100%. Bars are independent — they compare a
        program against its own relevant job market, not against each other, so they are not parts of a whole and
        will never add up to 100%.
      </p>
      <div className="mt-3" style={{ height: Math.max(320, chartData.length * 34) }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: 24, right: 40 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" domain={[0, 100]} ticks={[0, 20, 40, 60, 80, 100]} tickFormatter={(v) => `${v}%`} fontSize={12} />
            <YAxis type="category" dataKey="name" width={260} fontSize={11} interval={0} />
            <Tooltip formatter={(v) => `${Number(v).toFixed(1)}%`} />
            <Bar dataKey="score" radius={[0, 4, 4, 0]}>
              <LabelList dataKey="score" position="right" formatter={(v: React.ReactNode) => `${Number(v).toFixed(1)}%`} fontSize={11} />
              {chartData.map((d, i) => (
                <Cell key={i} fill={scoreColor(d.score)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-2 text-xs text-muted">
        👉 <Link href="/programs" className="font-medium text-primary">Browse the full list</Link> to filter, search,
        and open any program&apos;s detail page.
      </p>

      <hr className="my-6 border-border" />

      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        <div>
          <h2 className="text-lg font-semibold">🌟 Strongest programs</h2>
          <ul className="mt-3 space-y-4">
            {strongest.map((p) => (
              <li key={`${p.university}-${p.program}-${p.degree}`}>
                <div className="text-sm font-medium">
                  {p.program} ({p.degree}){isAllUniversities ? ` · ${uniAbbr(p.university)}` : ""}
                  {docScoreFor(p.program, p.degree) !== null && docScoreFor(p.program, p.degree)! < LOW_DOC_THRESHOLD && (
                    <span className="ml-2 rounded-full bg-orange-100 px-2 py-0.5 text-[10px] font-medium text-orange-700">
                      📝 Limited course data
                    </span>
                  )}
                </div>
                <div className="text-xs text-muted">
                  {formatScore(p.core_role_coverage_pct)} · {p.relevant_roles ?? ""}
                </div>
                <div className="mt-1 h-2 w-full rounded-full bg-surface">
                  <div
                    className="h-2 rounded-full"
                    style={{
                      width: `${Math.min(p.core_role_coverage_pct ?? 0, 100)}%`,
                      backgroundColor: scoreColor(p.core_role_coverage_pct),
                    }}
                  />
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h2 className="text-lg font-semibold">🔍 Most common gap skills</h2>
          <div className="mt-3" style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topGaps} layout="vertical" margin={{ left: 8, right: 20 }}>
                <XAxis type="number" fontSize={11} />
                <YAxis type="category" dataKey="skill" width={130} fontSize={11} interval={0} />
                <Tooltip />
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
