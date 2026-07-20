"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Sidebar } from "@/components/Sidebar";
import { TopBar } from "@/components/TopBar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted">
        <p>Loading…</p>
      </div>
    );
  }

  return (
    // h-screen + overflow-hidden keeps the sidebar painted to the full
    // window height; only <main> scrolls.
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-background px-8 py-6">
        <div className="mx-auto max-w-5xl">
          <TopBar />
          {children}
        </div>
      </main>
    </div>
  );
}
