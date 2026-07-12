"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api, ProgramAlignment } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ScoreDisplay } from "@/components/ScoreBadge";
import { rolesShort } from "@/lib/format";

export default function ProgramsPage() {
  const { currentUniversity } = useAuth();
  const [programs, setPrograms] = useState<ProgramAlignment[] | null>(null);
  const [degreeFilter, setDegreeFilter] = useState("All");
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (currentUniversity) api.programs(currentUniversity).then(setPrograms);
  }, [currentUniversity]);

  const degrees = useMemo(
    () => ["All", ...Array.from(new Set((programs ?? []).map((p) => p.degree)))],
    [programs]
  );

  const filtered = useMemo(() => {
    return (programs ?? [])
      .filter((p) => degreeFilter === "All" || p.degree === degreeFilter)
      .filter((p) => p.program.toLowerCase().includes(search.toLowerCase()))
      .sort((a, b) => (b.core_role_coverage_pct ?? -1) - (a.core_role_coverage_pct ?? -1));
  }, [programs, degreeFilter, search]);

  if (!programs) return <p className="text-muted">Loading…</p>;

  return (
    <div>
      <h1 className="text-3xl font-bold text-primary-dark">Programs</h1>
      <p className="mt-1 text-sm text-muted">Select a program to see its full alignment breakdown.</p>

      <div className="mt-5 flex flex-wrap gap-3">
        <select
          value={degreeFilter}
          onChange={(e) => setDegreeFilter(e.target.value)}
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm"
        >
          {degrees.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
        <input
          type="text"
          placeholder="e.g. Data Science, Information Security…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="min-w-64 flex-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm"
        />
      </div>

      <p className="mt-3 text-xs text-muted">Showing {filtered.length} programs</p>

      <ul className="mt-3 space-y-3">
        {filtered.map((p) => (
          <li key={`${p.program}-${p.degree}`} className="flex items-center justify-between rounded-xl border border-border p-4">
            <div>
              <div className="font-semibold">{p.program}</div>
              <div className="text-xs text-muted">
                {p.degree} · {rolesShort(p.relevant_roles)}
              </div>
            </div>
            <div className="flex items-center gap-6">
              <ScoreDisplay score={p.core_role_coverage_pct} size="md" />
              <Link
                href={`/programs/${encodeURIComponent(p.program)}/${encodeURIComponent(p.degree)}`}
                className="rounded-lg border border-border px-3 py-1.5 text-sm font-medium hover:bg-surface"
              >
                View →
              </Link>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
