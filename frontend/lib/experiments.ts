// Maps the 12 internal experiment codes ({TFIDF,KeyBERT,LLM}_{names,desc}_{exact,semantic})
// to plain-language names. Only the canonical experiment (LLM_desc_semantic)
// is ever shown to product users, but the raw code still leaks into a couple
// of admin/methodology spots — this keeps it human-readable wherever it does.

const EXTRACTION_METHOD: Record<string, string> = {
  TFIDF: "keyword-frequency (TF-IDF)",
  KeyBERT: "keyword-extraction (KeyBERT)",
  LLM: "AI-extracted (LLM)",
};

const INPUT_TYPE: Record<string, string> = {
  names: "course names only",
  desc: "full course descriptions",
};

const MATCHING: Record<string, string> = {
  exact: "exact text matching",
  semantic: "matching by meaning (semantic similarity)",
};

export function formatExperiment(code: string): string {
  const parts = code.split("_");
  if (parts.length !== 3) return code;
  const [method, input, matching] = parts;
  const methodLabel = EXTRACTION_METHOD[method];
  const inputLabel = INPUT_TYPE[input];
  const matchingLabel = MATCHING[matching];
  if (!methodLabel || !inputLabel || !matchingLabel) return code;
  return `${methodLabel} skills from ${inputLabel}, ${matchingLabel}`;
}

export const CANONICAL_EXPERIMENT = "LLM_desc_semantic";
