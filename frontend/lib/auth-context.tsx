"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, User } from "./api";

// Sentinel value for the admin "view every university at once" mode —
// pages translate it to an omitted `university` API param (the backend
// treats no-param from an admin account as "all universities").
export const ALL_UNIVERSITIES = "__ALL__";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  currentUniversity: string | null;
  /** What to pass as the `university` API param: undefined in ALL mode. */
  universityParam: string | undefined;
  isAllUniversities: boolean;
  canSwitchUniversity: boolean;
  switchUniversity: (university: string) => void;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

const UNIVERSITY_STORAGE_KEY = "cl_current_university";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentUniversity, setCurrentUniversity] = useState<string | null>(null);

  const canSwitchUniversity = user?.org_type === "policy" || user?.org_type === "internal";

  useEffect(() => {
    api
      .me()
      .then(({ user }) => {
        setUser(user);
        if (user.org_type === "university") {
          setCurrentUniversity(user.university_name);
        } else {
          const stored = typeof window !== "undefined" ? window.localStorage.getItem(UNIVERSITY_STORAGE_KEY) : null;
          setCurrentUniversity(stored);
        }
      })
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  // Admin accounts with no stored preference: default to the first
  // university once the list loads (mirrors the old Streamlit behavior of
  // defaulting to universities[0] on login).
  useEffect(() => {
    if (user && canSwitchUniversity && !currentUniversity) {
      api.universities().then((list) => {
        if (list.length) setCurrentUniversity(list[0]);
      });
    }
  }, [user, canSwitchUniversity, currentUniversity]);

  const switchUniversity = useCallback((university: string) => {
    setCurrentUniversity(university);
    if (typeof window !== "undefined") {
      window.localStorage.setItem(UNIVERSITY_STORAGE_KEY, university);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { user } = await api.login(email, password);
    setUser(user);
    setCurrentUniversity(user.org_type === "university" ? user.university_name : null);
  }, []);

  const logout = useCallback(async () => {
    await api.logout();
    setUser(null);
    setCurrentUniversity(null);
  }, []);

  const isAllUniversities = currentUniversity === ALL_UNIVERSITIES;
  const universityParam = isAllUniversities ? undefined : currentUniversity ?? undefined;

  return (
    <AuthContext.Provider
      value={{
        user, loading, currentUniversity, universityParam, isAllUniversities,
        canSwitchUniversity, switchUniversity, login, logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
