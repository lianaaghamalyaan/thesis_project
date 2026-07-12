"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export function UniversityBanner() {
  const { canSwitchUniversity, currentUniversity, switchUniversity, user } = useAuth();
  const [universities, setUniversities] = useState<string[]>([]);

  useEffect(() => {
    if (canSwitchUniversity) {
      api.universities().then(setUniversities);
    }
  }, [canSwitchUniversity]);

  if (!canSwitchUniversity) return null;

  return (
    <div className="mb-4 rounded-xl bg-gradient-to-br from-primary to-primary-dark px-5 py-3 text-white">
      <div className="text-xs font-semibold uppercase tracking-wide opacity-80">Admin view · currently viewing</div>
      <div className="mt-1 flex items-center justify-between gap-4">
        <select
          value={currentUniversity ?? ""}
          onChange={(e) => switchUniversity(e.target.value)}
          className="w-full max-w-md rounded-lg border-0 bg-white px-3 py-1.5 text-sm font-medium text-foreground"
        >
          {universities.map((u) => (
            <option key={u} value={u}>
              {u}
            </option>
          ))}
        </select>
        <span className="whitespace-nowrap text-xs opacity-90">👁️ Viewing as {user?.role}</span>
      </div>
    </div>
  );
}
