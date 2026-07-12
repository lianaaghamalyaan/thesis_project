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
};

export type LlmGapSkillRow = {
  university: string;
  program_name: string;
  degree_level: string;
  role_groups: string | null;
  missing_skill: string;
  job_frequency: number | null;
  category: string | null;
};

export type StrengthSkill = { skill: string; job_count: number };

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
  benchmark: BenchmarkResult | null;
  doc_score: number;
  gap_type: string;
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
    n_it_postings: number | null;
    n_sources: number | null;
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
};

export type Recommendation = { type: string; title: string; description: string; priority: string };

export type ProgramRecommendations = {
  program: string;
  degree: string;
  core_role_coverage_pct: number | null;
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

export type DocQualityProgram = { program: string; degree: string; n_courses: number; doc_score: number };

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
