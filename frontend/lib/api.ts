const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body.detail ?? res.statusText);
  }
  return res.json();
}

export type User = {
  user_id: number;
  email: string;
  full_name: string;
  role: string;
  org_id: number;
  org_name: string;
  org_type: "university" | "policy" | "internal";
  university_id: number | null;
  university_name: string | null;
};

export type ProgramAlignment = {
  experiment: string;
  university: string;
  program: string;
  degree: string;
  relevant_roles: string | null;
  source_url: string | null;
  n_program_skills: number | null;
  n_job_skills: number | null;
  n_overlap: number | null;
  full_coverage_pct: number | null;
  role_coverage_pct: number | null;
  core_role_coverage_pct: number | null;
  core_n_job_skills: number | null;
  core_n_overlap: number | null;
  core_n_gap: number | null;
  weighted_core_coverage_pct: number | null;
};

export type GapSkillRow = {
  university: string;
  program: string;
  degree: string;
  gap_skill: string;
  job_frequency: number | null;
  relevant_roles: string | null;
  pct_of_role_postings: number | null;
};

export type LlmGapSkillRow = {
  university: string;
  program_name: string;
  degree_level: string;
  role_groups: string | null;
  missing_skill: string;
  job_frequency: number | null;
  category: string | null;
  pct_of_role_postings: number | null;
};

// matched_program_skills is only populated on Program Detail's Strengths list
// (server/analytics.py::get_strengths); Job Fit's "missing" list reuses this
// type but never sets it (no reused meaning for "not covered").
export type StrengthSkill = {
  skill: string;
  job_count: number;
  pct_of_role_postings?: number | null;
  matched_program_skills?: string[];
};

// "What is this skill?" — server/api/routes/job_skills.py's /skills/info,
// generated once per skill (pipeline/generate_skill_info.py) since the
// target users (CLAUDE.md: non-technical academic leadership) shouldn't be
// expected to already know what e.g. "TypeScript" or "CI/CD" are. A skill
// with no entry yet (generation runs incrementally) is simply absent.
export type SkillInfo = { description: string; where_used: string };

export type SkillCourse = { course_name: string; high_confidence: boolean };

export type ExtractedSkillEvidence = {
  skill_name: string;
  confidence_tier: string | null;
  extraction_method: string;
  input_type: string | null;
};

export type CourseEvidence = {
  course_name: string;
  course_name_original: string | null;
  credits: number | null;
  description: string | null;
  source_url: string | null;
  source_language: string | null;
  notes: string | null;
  skills: ExtractedSkillEvidence[];
};

export type ProgramOutcomeEvidence = {
  outcome_text: string;
  outcome_text_original: string | null;
  source_url: string | null;
  source_language: string | null;
  is_official: boolean;
  skills: ExtractedSkillEvidence[];
};

export type BenchmarkResult = {
  peer_mean: number;
  peer_median: number;
  peer_max: number;
  peer_n: number;
  matched_on: string;
};

export type ProgramDetail = {
  alignment: ProgramAlignment | null;
  gaps: LlmGapSkillRow[];
  fallback_gaps: GapSkillRow[];
  strengths: StrengthSkill[];
  skill_courses: Record<string, SkillCourse[]>;
  benchmark: BenchmarkResult | null;
  doc_score: number;
  gap_type: string;
  course_evidence: CourseEvidence[];
  program_outcomes: ProgramOutcomeEvidence[];
};

export type RunMetadata = {
  run_id: string;
  is_canonical: boolean;
  experiment: string;
  created_at: string;
  curriculum_snapshot: {
    collected_at: string | null;
    n_universities: number | null;
    n_programs: number | null;
    n_courses: number | null;
  };
  job_snapshot: {
    collected_at: string | null;
    earliest_at: string | null;
    n_it_postings: number | null;
    n_sources: number | null;
    n_unknown_date: number | null;
    window: string | null;
  };
  esco_version: string | null;
  notes: string | null;
};

export const api = {
  login: (email: string, password: string) =>
    request<{ user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  logout: () => request<{ ok: boolean }>("/auth/logout", { method: "POST" }),
  me: () => request<{ user: User }>("/auth/me"),
  universities: () => request<string[]>("/universities"),
  programs: (university?: string) =>
    request<ProgramAlignment[]>(`/programs${university ? `?university=${encodeURIComponent(university)}` : ""}`),
  programDetail: (program: string, degree: string, university?: string) =>
    request<ProgramDetail>(
      `/programs/${encodeURIComponent(program)}/${encodeURIComponent(degree)}${
        university ? `?university=${encodeURIComponent(university)}` : ""
      }`
    ),
  gaps: (university?: string) =>
    request<GapSkillRow[]>(`/gaps${university ? `?university=${encodeURIComponent(university)}` : ""}`),
  runMetadata: () => request<RunMetadata>("/run-metadata"),
  allUniversities: () => request<ProgramAlignment[]>("/all-universities"),
  recommendations: (university?: string) =>
    request<RecommendationsResponse>(
      `/recommendations${university ? `?university=${encodeURIComponent(university)}` : ""}`
    ),
  jobFitRoles: () => request<string[]>("/job-fit/roles"),
  skillsInfo: (names: string[]) =>
    names.length
      ? request<Record<string, SkillInfo>>(`/skills/info?names=${encodeURIComponent(names.join(","))}`)
      : Promise.resolve({}),
  jobFit: (program: string, degree: string, role: string, university?: string) =>
    request<JobFitResult>(
      `/job-fit?program=${encodeURIComponent(program)}&degree=${encodeURIComponent(degree)}&role=${encodeURIComponent(role)}` +
        (university ? `&university=${encodeURIComponent(university)}` : "")
    ),
  docQuality: (university?: string) =>
    request<DocQualityResponse>(`/admin/doc-quality${university ? `?university=${encodeURIComponent(university)}` : ""}`),
  programBriefPdfUrl: (program: string, degree: string, university?: string) =>
    `${API_BASE}/programs/${encodeURIComponent(program)}/${encodeURIComponent(degree)}/brief.pdf${
      university ? `?university=${encodeURIComponent(university)}` : ""
    }`,
  curriculumEditor: () => request<EditorProgram[]>("/admin/curriculum-editor"),
  createAssertion: (course_id: number, skill_name: string, evidence_note?: string) =>
    request<{ id: number; skill_name: string }>("/admin/assertions", {
      method: "POST",
      body: JSON.stringify({ course_id, skill_name, evidence_note: evidence_note ?? null }),
    }),
  deleteAssertion: (assertion_id: number) =>
    request<{ ok: boolean }>(`/admin/assertions/${assertion_id}`, { method: "DELETE" }),
  evidenceMeta: () => request<EvidenceMeta>("/evidence/meta"),
  evidenceJobs: (params: { q?: string; role?: string; source?: string; offset?: number; limit?: number }) => {
    const qp = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) if (v !== undefined && v !== "") qp.set(k, String(v));
    return request<EvidenceJobsResponse>(`/evidence/jobs?${qp}`);
  },
  evidenceCourses: (params: { q?: string; university?: string; offset?: number; limit?: number }) => {
    const qp = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) if (v !== undefined && v !== "") qp.set(k, String(v));
    return request<EvidenceCoursesResponse>(`/evidence/courses?${qp}`);
  },
  coveragePreview: (program: string, degree: string) =>
    request<CoveragePreview>(
      `/admin/coverage-preview?program=${encodeURIComponent(program)}&degree=${encodeURIComponent(degree)}`
    ),
};

export type Recommendation = { type: string; title: string; description: string; priority: string };

export type ProgramRecommendations = {
  program: string;
  degree: string;
  weighted_core_coverage_pct: number | null;
  doc_score: number;
  gap_type: string;
  recommendations: Recommendation[];
};

export type CrossProgramGap = { gap_skill: string; n_programs: number; total_frequency: number };

export type RecommendationsResponse = {
  programs: ProgramRecommendations[];
  cross_program_gaps: CrossProgramGap[];
};

export type MatchedSkill = { skill: string; job_count: number; is_core: boolean };

export type JobFitResult = {
  match_score: number | null;
  weighted_score: number | null;
  matched: MatchedSkill[];
  missing: StrengthSkill[];
  n_core_skills: number;
  n_role_skills: number;
  n_program_skills: number;
  n_role_postings: number;
};

export type DocumentationLevel = "no_published_data" | "minimal" | "partial" | "full";

export type DocQualityProgram = {
  university: string;
  program: string;
  degree: string;
  n_courses: number;
  doc_score: number;
  documentation_level: DocumentationLevel;
  n_missing: number;
  n_ai_generated: number;
  n_short: number;
  n_full: number;
};

export type MissingDescriptionCourse = {
  program_name: string;
  degree_level: string;
  course_name: string;
  description: string | null;
};

export type DocQualityResponse = {
  programs: DocQualityProgram[];
  missing_descriptions: MissingDescriptionCourse[];
};

// ── "My Curriculum" editor (university admins confirming taught skills) ───

export type SkillAssertion = {
  id: number;
  skill_name: string;
  asserted_by: string;
  asserted_at: string;
  evidence_note: string | null;
};

export type EditorCourse = {
  course_id: number;
  course_name: string;
  extracted_skills: string[];
  assertions: SkillAssertion[];
};

export type EditorProgram = {
  program: string;
  degree: string;
  courses: EditorCourse[];
};

export type CoveragePreview = {
  core_n_job_skills: number | null;
  current_core_n_overlap: number | null;
  current_core_role_coverage_pct: number | null;
  current_weighted_core_coverage_pct: number | null;
  with_assertions_core_n_overlap: number | null;
  with_assertions_core_role_coverage_pct: number | null;
  with_assertions_weighted_core_coverage_pct: number | null;
};

// ── Evidence Explorer (audit the raw records behind every score) ──────────

export type EvidenceMeta = {
  extraction_run: {
    run_key: string;
    model_name: string;
    prompt_version: string;
    status: string;
    completed_at: string | null;
  } | null;
  role_groups: string[];
  sources: string[];
  universities: string[];
};

export type EvidenceJobSkill = {
  skill_name: string;
  raw_skill_name: string;
  evidence_text: string;
  evidence_type: string;
};

export type EvidencePosting = {
  posting_id: number;
  job_id: string;
  job_title: string;
  company_name: string | null;
  location: string | null;
  employment_type: string | null;
  seniority_level: string | null;
  posting_date: string | null;
  deadline: string | null;
  it_role_group: string | null;
  source_name: string;
  source_type: string;
  source_url: string;
  skills: EvidenceJobSkill[];
};

export type EvidenceJobsResponse = { total: number; run_key: string | null; postings: EvidencePosting[] };

export type EvidenceCourseSkill = {
  skill_name: string;
  confidence_tier: string | null;
  extraction_method: string;
  input_type: string;
};

export type EvidenceCourse = {
  course_id: number;
  course_name: string;
  course_name_original: string | null;
  university: string;
  program: string;
  degree: string;
  credits: number | null;
  description: string | null;
  ai_generated: boolean;
  source_url: string | null;
  skills: EvidenceCourseSkill[];
};

export type EvidenceCoursesResponse = { total: number; courses: EvidenceCourse[] };
