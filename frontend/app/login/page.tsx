"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { ApiError } from "@/lib/api";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      router.push("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface px-4">
      <div className="w-full max-w-md">
        <h1 className="font-display text-3xl font-bold text-primary-dark">CurriculumLens</h1>
        <p className="mt-1 text-sm text-muted">Curriculum – labor market alignment for Armenian universities</p>

        <form onSubmit={handleSubmit} className="mt-6 rounded-xl border border-border bg-white p-6 shadow-sm">
          <label className="block text-sm font-medium text-foreground">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 mb-4 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm outline-none focus:border-primary"
          />

          <label className="block text-sm font-medium text-foreground">Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 mb-4 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm outline-none focus:border-primary"
          />

          {error && <p className="mb-4 text-sm text-score-developing">{error}</p>}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-primary py-2 text-sm font-semibold text-white hover:bg-primary-dark disabled:opacity-60"
          >
            {submitting ? "Logging in…" : "Log in"}
          </button>
        </form>
      </div>
    </div>
  );
}
