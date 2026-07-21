"use client";

import { useEffect, useMemo, useState } from "react";
import { api, EditorProgram, CoveragePreview, GapSkillRow } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { formatScore, scoreColor } from "@/lib/format";

// "My Curriculum" — the university's own org_admin confirms a course teaches
// a skill the extraction missed (e.g. a thin published description). Kept
// deliberately separate from the canonical AlignmentResult: confirmations
// show up here as a live "with your confirmations" preview, not a silent
// change to the score everyone else sees. See server/api/routes/curriculum_editor.py.
//
// The skill pickers lead with this program's *market gap skills* (demanded by
// the relevant roles but not currently covered) because those are the ones
// whose confirmation actually moves coverage — an already-extracted skill is
// already counted, so confirming it is a no-op for the score. Any skill can
// still be typed in free-text for the cases the gap list doesn't cover.

type SkillOptions = { gaps: string[]; others: string[] };

export default function MyCurriculumPage() {
  const { user } = useAuth();
  const [data, setData] = useState<EditorProgram[]>([]);
  const [gaps, setGaps] = useState<GapSkillRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<{ program: string; degree: string } | null>(null);
  const [tab, setTab] = useState<"courses" | "gaps">("gaps");
  const [preview, setPreview] = useState<CoveragePreview | null>(null);
  const [busyKey, setBusyKey] = useState<string | null>(null);

  // Only the editor list toggles the full-page "Loading…"; assertion writes
  // refetch it in the background (see reloadData) so the editor doesn't blank
  // out on every click.
  const load = () => {
    setLoading(true);
    Promise.all([api.curriculumEditor(), api.gaps()])
      .then(([d, g]) => {
        setData(d);
        setGaps(g);
        if (d.length && !selected) setSelected({ program: d[0].program, degree: d[0].degree });
      })
      .finally(() => setLoading(false));
  };

  const reloadData = () => api.curriculumEditor().then(setData);

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const program = useMemo(
    () => data.find((p) => p.program === selected?.program && p.degree === selected?.degree) ?? null,
    [data, selected]
  );

  const refreshPreview = () => {
    if (program) api.coveragePreview(program.program, program.degree).then(setPreview);
  };

  useEffect(() => {
    if (!program) return;
    setPreview(null);
    api.coveragePreview(program.program, program.degree).then(setPreview);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [program?.program, program?.degree]);

  // Market gap skills for the selected program, highest-demand first — the
  // skills that would actually raise coverage if confirmed as taught.
  const programGapRows = useMemo(() => {
    if (!program) return [] as GapSkillRow[];
    return gaps
      .filter((g) => g.program === program.program && g.degree === program.degree)
      .sort((a, b) => (b.job_frequency ?? 0) - (a.job_frequency ?? 0));
  }, [gaps, program]);
  const programGapSkills = useMemo(() => programGapRows.map((g) => g.gap_skill), [programGapRows]);

  // Everything else already extracted somewhere in this university, as a
  // secondary group (mostly no-ops for the score, but useful for completeness).
  const otherExtractedSkills = useMemo(() => {
    const set = new Set<string>();
    for (const p of data) for (const c of p.courses) for (const s of c.extracted_skills) set.add(s);
    for (const s of programGapSkills) set.delete(s); // don't list a skill in both groups
    return [...set].sort();
  }, [data, programGapSkills]);

  const options: SkillOptions = { gaps: programGapSkills, others: otherExtractedSkills };

  if (user && user.role !== "org_admin") {
    return (
      <div>
        <h1 className="font-display text-3xl font-bold text-primary-dark">My Curriculum</h1>
        <p className="mt-4 rounded-lg bg-surface px-4 py-3 text-sm text-muted">
          This page is only available to a university's curriculum-editor account.
        </p>
      </div>
    );
  }

  async function addAssertionWithNote(courseId: number, skillName: string, note?: string) {
    const key = `${courseId}:${skillName}`;
    setBusyKey(key);
    try {
      await api.createAssertion(courseId, skillName, note);
      await reloadData();
      refreshPreview();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to add");
    } finally {
      setBusyKey(null);
    }
  }

  async function addAssertion(courseId: number, skillName: string) {
    const key = `${courseId}:${skillName}`;
    setBusyKey(key);
    try {
      await api.createAssertion(courseId, skillName);
      await reloadData();
      refreshPreview();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to add");
    } finally {
      setBusyKey(null);
    }
  }

  async function removeAssertion(assertionId: number) {
    setBusyKey(`del:${assertionId}`);
    try {
      await api.deleteAssertion(assertionId);
      await reloadData();
      refreshPreview();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to remove");
    } finally {
      setBusyKey(null);
    }
  }

  return (
    <div>
      <h1 className="font-display text-3xl font-bold text-primary-dark">My Curriculum</h1>
      <p className="mt-1 text-sm text-muted">
        Confirm a skill is taught in a course even if the published description doesn't mention it. Confirmations are
        shown separately from the official alignment score below — they don't change it automatically.
      </p>

      {loading && <p className="mt-6 text-sm text-muted">Loading…</p>}

      {!loading && data.length > 0 && (
        <>
          <div className="mt-5 flex flex-wrap gap-3">
            <select
              value={selected ? `${selected.program}|${selected.degree}` : ""}
              onChange={(e) => {
                const [p, d] = e.target.value.split("|");
                setSelected({ program: p, degree: d });
              }}
              className="min-w-64 rounded-lg border border-border bg-surface px-3 py-2 text-sm"
            >
              {data.map((p) => (
                <option key={`${p.program}-${p.degree}`} value={`${p.program}|${p.degree}`}>
                  {p.program} ({p.degree})
                </option>
              ))}
            </select>
          </div>

          {preview && (
            <div className="mt-5 flex flex-wrap items-center gap-6 rounded-xl border border-border bg-surface p-5">
              <div className="text-center">
                <div className="text-xs text-muted">Current (official)</div>
                <div className="text-2xl font-bold" style={{ color: scoreColor(preview.current_weighted_core_coverage_pct) }}>
                  {formatScore(preview.current_weighted_core_coverage_pct)}
                </div>
              </div>
              <div className="text-2xl text-muted">→</div>
              <div className="text-center">
                <div className="text-xs text-muted">With your confirmations</div>
                <div
                  className="text-2xl font-bold"
                  style={{ color: scoreColor(preview.with_assertions_weighted_core_coverage_pct) }}
                >
                  {formatScore(preview.with_assertions_weighted_core_coverage_pct)}
                </div>
              </div>
              <div className="text-sm text-muted">
                {preview.with_assertions_core_n_overlap ?? 0} of {preview.core_n_job_skills ?? 0} core skills covered
                with confirmations, vs {preview.current_core_n_overlap ?? 0} today. The "current" figure is your
                official score; the projection adds only the estimated effect of your confirmations and isn't saved —
                it becomes official on the next data refresh.
              </div>
            </div>
          )}

          <div className="mt-6 flex gap-2 border-b border-border">
            <button
              onClick={() => setTab("courses")}
              className={`px-3 py-2 text-sm font-medium ${tab === "courses" ? "border-b-2 border-primary-dark text-primary-dark" : "text-muted"}`}
            >
              Per-course view
            </button>
            <button
              onClick={() => setTab("gaps")}
              className={`px-3 py-2 text-sm font-medium ${tab === "gaps" ? "border-b-2 border-primary-dark text-primary-dark" : "text-muted"}`}
            >
              Gap work queue ({programGapRows.length})
            </button>
          </div>

          {program && tab === "courses" && (
            <div className="mt-4 space-y-3">
              {program.courses.map((course) => (
                <div key={course.course_id} className="rounded-lg border border-border p-4">
                  <div className="font-medium">{course.course_name}</div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {course.extracted_skills.map((s) => (
                      <span key={s} className="rounded-full bg-surface px-2.5 py-1 text-xs">
                        {s}
                      </span>
                    ))}
                    {course.assertions.map((a) => (
                      <span
                        key={a.id}
                        className="flex items-center gap-1.5 rounded-full border border-primary-dark/30 bg-primary-dark/5 px-2.5 py-1 text-xs"
                        title={`Confirmed by ${a.asserted_by} on ${a.asserted_at.slice(0, 10)}`}
                      >
                        ✓ {a.skill_name}
                        <button
                          onClick={() => removeAssertion(a.id)}
                          disabled={busyKey === `del:${a.id}`}
                          className="text-muted hover:text-red-600"
                          aria-label={`Remove ${a.skill_name}`}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                    {course.extracted_skills.length === 0 && course.assertions.length === 0 && (
                      <span className="text-xs text-muted">No skills extracted yet.</span>
                    )}
                  </div>
                  <CourseSkillPicker
                    course={course}
                    options={options}
                    busyKey={busyKey}
                    onAdd={(skill) => addAssertion(course.course_id, skill)}
                  />
                </div>
              ))}
            </div>
          )}

          {program && tab === "gaps" && (
            <GapWorkQueue
              gapRows={programGapRows}
              courses={program.courses}
              busyKey={busyKey}
              onAdd={addAssertionWithNote}
              onRemove={removeAssertion}
            />
          )}
        </>
      )}

      {!loading && data.length === 0 && <p className="mt-6 text-sm text-muted">No programs found for your university.</p>}
    </div>
  );
}

// A <select> whose options are grouped into "market gaps" (score-moving) and
// "other skills", excluding anything in `exclude`. Returns the chosen value
// via onPick and resets itself to the placeholder.
function GroupedSkillSelect({
  options,
  exclude,
  placeholder,
  onPick,
}: {
  options: SkillOptions;
  exclude: Set<string>;
  placeholder: string;
  onPick: (skill: string) => void;
}) {
  const gaps = useMemo(() => options.gaps.filter((s) => !exclude.has(s)), [options.gaps, exclude]);
  const others = useMemo(() => options.others.filter((s) => !exclude.has(s)), [options.others, exclude]);

  return (
    <select
      value=""
      onChange={(e) => {
        if (e.target.value) onPick(e.target.value);
      }}
      className="min-w-56 rounded-lg border border-border bg-white px-2 py-1 text-xs"
    >
      <option value="">{placeholder}</option>
      {gaps.length > 0 && (
        <optgroup label="Market gaps (raise coverage)">
          {gaps.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </optgroup>
      )}
      {others.length > 0 && (
        <optgroup label="Other skills">
          {others.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </optgroup>
      )}
    </select>
  );
}

function CourseSkillPicker({
  course,
  options,
  busyKey,
  onAdd,
}: {
  course: EditorProgram["courses"][number];
  options: SkillOptions;
  busyKey: string | null;
  onAdd: (skill: string) => void;
}) {
  const [custom, setCustom] = useState("");
  const already = useMemo(
    () => new Set([...course.extracted_skills, ...course.assertions.map((a) => a.skill_name)]),
    [course]
  );

  return (
    <div className="mt-3 flex flex-wrap items-center gap-2">
      <GroupedSkillSelect
        options={options}
        exclude={already}
        placeholder="+ confirm a skill…"
        onPick={onAdd}
      />
      <input
        value={custom}
        onChange={(e) => setCustom(e.target.value)}
        placeholder="or type a new skill name"
        className="rounded-lg border border-border bg-white px-2 py-1 text-xs"
      />
      <button
        onClick={() => {
          const s = custom.trim();
          if (!s) return;
          setCustom("");
          onAdd(s);
        }}
        disabled={!custom.trim() || busyKey !== null}
        className="rounded-lg bg-primary-dark px-2.5 py-1 text-xs font-medium text-white disabled:opacity-40"
      >
        Add
      </button>
    </div>
  );
}

// The gap-driven work queue: this program's market gap skills, highest
// demand first. Every confirmation still lands on a specific course — the
// queue only changes where you start (the market's most-wanted skills),
// not the evidence standard.
function GapWorkQueue({
  gapRows,
  courses,
  busyKey,
  onAdd,
  onRemove,
}: {
  gapRows: GapSkillRow[];
  courses: EditorProgram["courses"];
  busyKey: string | null;
  onAdd: (courseId: number, skill: string, note?: string) => void;
  onRemove: (assertionId: number) => void;
}) {
  // skill -> the assertion(s) already claiming it, with their course names.
  const assertedBySkill = useMemo(() => {
    const map = new Map<string, { id: number; course: string; by: string; at: string }[]>();
    for (const c of courses)
      for (const a of c.assertions)
        map.set(a.skill_name, [...(map.get(a.skill_name) ?? []), { id: a.id, course: c.course_name, by: a.asserted_by, at: a.asserted_at }]);
    return map;
  }, [courses]);

  const nAsserted = useMemo(() => courses.reduce((n, c) => n + c.assertions.length, 0), [courses]);
  const maxFreq = Math.max(1, ...gapRows.map((g) => g.job_frequency ?? 0));

  return (
    <div className="mt-4">
      <p className="max-w-3xl text-sm leading-relaxed text-muted">
        These are the skills the market demands from this program&apos;s relevant roles that we could not find in any
        course description — ordered by demand, so the top of the list is where a confirmation raises your coverage
        most. If a skill <em>is</em> taught, pick the course that teaches it.
      </p>

      {nAsserted > 0 && (
        <p className="mt-3 max-w-3xl rounded-lg bg-accent-soft px-3 py-2 text-xs leading-relaxed text-foreground">
          📌 {nAsserted} skill{nAsserted === 1 ? " is" : "s are"} currently self-reported but not in any published
          course description. Self-reported skills stay visibly separate from extracted ones — the durable fix is to
          update the official course descriptions so the next data refresh finds them on its own.
        </p>
      )}

      <ul className="mt-4 space-y-2">
        {gapRows.map((g) => {
          const asserted = assertedBySkill.get(g.gap_skill) ?? [];
          return (
            <li key={g.gap_skill} className="rounded-lg border border-border bg-surface px-4 py-3">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <span className="text-sm font-medium">{g.gap_skill}</span>
                <span className="flex items-center gap-3 text-xs text-muted">
                  <span className="hidden h-1.5 w-24 overflow-hidden rounded-full bg-surface-muted sm:block" aria-hidden>
                    <span
                      className="block h-full rounded-full bg-primary/70"
                      style={{ width: `${((g.job_frequency ?? 0) / maxFreq) * 100}%` }}
                    />
                  </span>
                  {g.job_frequency ?? 0} postings
                  {g.pct_of_role_postings != null && ` (${g.pct_of_role_postings}% of role postings)`}
                </span>
              </div>

              {asserted.length > 0 ? (
                <div className="mt-2 flex flex-wrap gap-2">
                  {asserted.map((a) => (
                    <span
                      key={a.id}
                      title={`Self-reported by ${a.by} on ${a.at.slice(0, 10)}`}
                      className="inline-flex items-center gap-1.5 rounded-full border border-primary-dark/30 bg-primary-dark/5 px-2.5 py-1 text-xs"
                    >
                      ✓ taught in <strong>{a.course}</strong>
                      <span className="rounded-full bg-accent-soft px-1.5 text-[10px] text-foreground">self-reported</span>
                      <button
                        onClick={() => onRemove(a.id)}
                        disabled={busyKey === `del:${a.id}`}
                        className="text-muted hover:text-red-600"
                        aria-label={`Remove confirmation for ${g.gap_skill}`}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              ) : (
                <GapRowPicker
                  skill={g.gap_skill}
                  courses={courses}
                  busy={busyKey !== null}
                  onAdd={onAdd}
                />
              )}
            </li>
          );
        })}
        {gapRows.length === 0 && (
          <p className="text-sm text-muted">No gap skills for this program — every core market skill is already covered.</p>
        )}
      </ul>
    </div>
  );
}

function GapRowPicker({
  skill,
  courses,
  busy,
  onAdd,
}: {
  skill: string;
  courses: EditorProgram["courses"];
  busy: boolean;
  onAdd: (courseId: number, skill: string, note?: string) => void;
}) {
  const [courseId, setCourseId] = useState<number | "">("");
  const [note, setNote] = useState("");

  return (
    <div className="mt-2 flex flex-wrap items-center gap-2">
      <select
        value={courseId}
        onChange={(e) => setCourseId(e.target.value ? Number(e.target.value) : "")}
        aria-label={`Course that teaches ${skill}`}
        className="min-w-56 rounded-lg border border-border bg-white px-2 py-1 text-xs"
      >
        <option value="">Taught somewhere? Pick the course…</option>
        {courses.map((c) => (
          <option key={c.course_id} value={c.course_id}>
            {c.course_name}
          </option>
        ))}
      </select>
      {courseId !== "" && (
        <>
          <input
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="evidence note (optional): topic, week, lab…"
            className="min-w-64 rounded-lg border border-border bg-white px-2 py-1 text-xs"
          />
          <button
            onClick={() => onAdd(Number(courseId), skill, note.trim() || undefined)}
            disabled={busy}
            className="rounded-lg bg-primary-dark px-2.5 py-1 text-xs font-medium text-white disabled:opacity-40"
          >
            Confirm taught
          </button>
        </>
      )}
    </div>
  );
}
