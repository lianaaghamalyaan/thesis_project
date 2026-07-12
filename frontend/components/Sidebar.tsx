"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

const NAV_SECTIONS: { title: string; items: { href: string; label: string; icon: string }[] }[] = [
  { title: "Methodology", items: [{ href: "/methodology", label: "Methodology", icon: "📐" }] },
  {
    title: "Dashboard",
    items: [
      { href: "/", label: "Overview", icon: "🏠" },
      { href: "/programs", label: "Programs", icon: "📚" },
      { href: "/recommendations", label: "Recommendations", icon: "🧭" },
      { href: "/job-fit", label: "Job Fit", icon: "💼" },
    ],
  },
  { title: "About", items: [{ href: "/admin", label: "Data & Admin", icon: "⚙️" }] },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, canSwitchUniversity, logout } = useAuth();

  return (
    <aside className="flex h-full w-60 shrink-0 flex-col bg-primary-dark px-4 py-5 text-white">
      <div className="mb-6 text-lg font-bold">📊 CurriculumLens</div>

      <nav className="flex-1 space-y-5">
        {NAV_SECTIONS.map((section) => (
          <div key={section.title}>
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-white/60">{section.title}</div>
            <ul className="space-y-0.5">
              {section.items.map((item) => {
                const active = pathname === item.href;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm ${
                        active ? "bg-white/15 font-medium" : "hover:bg-white/10"
                      }`}
                    >
                      <span>{item.icon}</span>
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
        {canSwitchUniversity && (
          <div>
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-white/60">Admin</div>
            <ul className="space-y-0.5">
              <li>
                <Link
                  href="/all-universities"
                  className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm ${
                    pathname === "/all-universities" ? "bg-white/15 font-medium" : "hover:bg-white/10"
                  }`}
                >
                  🌍 All Universities
                </Link>
              </li>
            </ul>
          </div>
        )}
      </nav>

      {user && (
        <div className="mt-auto border-t border-white/15 pt-4 text-sm">
          <div className="font-medium">{user.full_name}</div>
          <div className="text-xs text-white/60">
            {user.org_name} · {user.role}
          </div>
          <button
            onClick={() => logout()}
            className="mt-3 w-full rounded-lg border border-white/20 bg-white/10 py-1.5 text-xs hover:bg-white/20"
          >
            Log out
          </button>
        </div>
      )}
    </aside>
  );
}
