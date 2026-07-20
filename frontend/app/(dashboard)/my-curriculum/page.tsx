"use client";

import { useEffect, useMemo, useState } from "react";
import { api, EditorProgram, CoveragePreview } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { formatScore, scoreColor } from "@/lib/format";

// "My Curriculum" — the university's own org_admin confirms a course teaches
// a skill the extraction missed (e.g. a thin published description). Kept
// deliberately separate from the canonical AlignmentResult: confirmations
// show up here as a live "with your confirmations" preview, not a silent
// change to the score everyone else sees. See server/api/routes/curriculum_editor.py.

export default function MyCurriculumPage() {
  const { user } = useAuth();
  const [data, setData] = useState<EditorProgram[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<{ program: string; degree: string } | null>(null);
  const [tab, setTab] = useState<"courses" | "gaps">("courses");
  const [preview, setPreview] = useState<CoveragePreview | null>(null);
  const [busyKey, setBusyKey] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    api
      .curriculumEditor()
      .then((d) => {
        setData(d);
        if (d.length && !selected) setSelected({ program: d[0].program, degree: d[0].degree });
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const program = useMemo(
    () => data.find((p) => p.program === selected?.program && p.degree === selected?.degree) ?? null,
    [data, selected]
  );

  useEffect(() => {
    if (!program) return;
    setPreview(null);
    api.coveragePreview(program.program, program.degree).then(setPreview);
  }, [program]);

  if (user && user.role !== "org_admin") {
    return (
      <div>
        <h1 className="text-3xl font-bold text-primary-dark">My Curriculum</h1>
        <p className="mt-4 rounded-lg bg-surface px-4 py-3 text-sm text-muted">
          This page is only available to a university's curriculum-editor account.
        </p>
      </div>
    );
  }

  const refreshPreview = () => {
    if (program) api.coveragePreview(program.program, program.degree).then(setPreview);
  };

  const allExtractedSkills = useMemo(() => {
    const set = new Set<string>();
    for (const p of data) for (const c of p.courses) for (const s of c.extracted_skills) set.add(s);
    return set;
  }, [data]);

  async function addAssertion(courseId: number, skillName: string) {
    const key = `${courseId}:${skillName}`;
    setBusyKey(key);
    try {
      await api.createAssertion(courseId, skillName);
      load();
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
      load();
      refreshPreview();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to remove");
    } finally {
      setBusyKey(null);
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-primary-dark">My Curriculum</h1>
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
                <div className="text-xs text-muted">Current</div>
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
                with confirmations, vs {preview.current_core_n_overlap ?? 0} today. This preview is not saved anywhere
                — it recomputes live and only becomes the official score on the next data refresh.
              </div>
            </div>
          )}

          <div className="mt-6 flex gap-2 border-b border-border">
            <button
              onClick={() => setTab("courses")}
              className={`px-3 py-2 text-sm font-medium ${tab === "courses" ? "border-b-2 border-primary-dark text-primary-dark" : "text-muted"}`}
            >
              Per-course
            </button>
            <button
              onClick={() => setTab("gaps")}
              className={`px-3 py-2 text-sm font-medium ${tab === "gaps" ? "border-b-2 border-primary-dark text-primary-dark" : "text-muted"}`}
            >
              Choose from all skills
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
                    allSkills={allExtractedSkills}
                    busyKey={busyKey}
                    onAdd={(skill) => addAssertion(course.course_id, skill)}
                  />
                </div>
              ))}
            </div>
          )}

          {program && tab === "gaps" && (
            <div className="mt-4 rounded-lg border border-border p-4">
              <p className="text-sm text-muted">
                Pick a course, then confirm any skill from the full vocabulary — useful when a skill is taught but you
                don't want to hunt through the per-course list above.
              </p>
              <GeneralSkillPicker
                courses={program.courses}
                allSkills={allExtractedSkills}
                busyKey={busyKey}
                onAdd={addAssertion}
              />
            </div>
          )}
        </>
      )}

      {!loading && data.length === 0 && <p className="mt-6 text-sm text-muted">No programs found for your university.</p>}
    </div>
  );
}

function CourseSkillPicker({
  course,
  allSkills,
  busyKey,
  onAdd,
}: {
  course: EditorProgram["courses"][number];
  allSkills: Set<string>;
  busyKey: string | null;
  onAdd: (skill: string) => void;
}) {
  const [custom, setCustom] = useState("");
  const already = new Set([...course.extracted_skills, ...course.assertions.map((a) => a.skill_name)]);
  const options = useMemo(() => [...allSkills].filter((s) => !already.has(s)).sort(), [allSkills, already]);

  return (
    <div className="mt-3 flex flex-wrap items-center gap-2">
      <select
        value=""
        onChange={(e) => {
          if (e.target.value) onAdd(e.target.value);
        }}
        className="rounded-lg border border-border bg-white px-2 py-1 text-xs"
      >
        <option value="">+ confirm existing skill…</option>
        {options.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>
      <input
        value={custom}
        onChange={(e) => setCustom(e.target.value)}
        placeholder="or type a new skill name"
        className="rounded-lg border border-border bg-white px-2 py-1 text-xs"
      />
      <button
        onClick={() => {
          if (!custom.trim()) return;
          onAdd(custom.trim());
          setCustom("");
        }}
        disabled={!custom.trim() || busyKey === `${course.course_id}:${custom.trim()}`}
        className="rounded-lg bg-primary-dark px-2.5 py-1 text-xs font-medium text-white disabled:opacity-40"
      >
        Add
      </button>
    </div>
  );
}

function GeneralSkillPicker({
  courses,
  allSkills,
  busyKey,
  onAdd,
}: {
  courses: EditorProgram["courses"];
  allSkills: Set<string>;
  busyKey: string | null;
  onAdd: (courseId: number, skill: string) => void;
}) {
  const [courseId, setCourseId] = useState<number | "">(courses[0]?.course_id ?? "");
  const [skill, setSkill] = useState("");
  const sortedSkills = useMemo(() => [...allSkills].sort(), [allSkills]);

  return (
    <div className="mt-3 flex flex-wrap items-center gap-2">
      <select
        value={courseId}
        onChange={(e) => setCourseId(Number(e.target.value))}
        className="min-w-56 rounded-lg border border-border bg-white px-2 py-1 text-xs"
      >
        {courses.map((c) => (
          <option key={c.course_id} value={c.course_id}>
            {c.course_name}
          </option>
        ))}
      </select>
      <select
        value={skill}
        onChange={(e) => setSkill(e.target.value)}
        className="min-w-56 rounded-lg border border-border bg-white px-2 py-1 text-xs"
      >
        <option value="">Choose a skill…</option>
        {sortedSkills.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>
      <button
        onClick={() => {
          if (courseId && skill) onAdd(Number(courseId), skill);
        }}
        disabled={!courseId || !skill || busyKey === `${courseId}:${skill}`}
        className="rounded-lg bg-primary-dark px-2.5 py-1 text-xs font-medium text-white disabled:opacity-40"
      >
        Confirm taught
      </button>
    </div>
  );
}
