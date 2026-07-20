"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpenCheck,
  Briefcase,
  Compass,
  Globe,
  GraduationCap,
  LayoutDashboard,
  PencilLine,
  Settings,
  type LucideIcon,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";

type NavItem = { href: string; label: string; icon: LucideIcon };
type NavSection = { title: string; items: NavItem[]; show?: (ctx: { canSwitchUniversity: boolean; role?: string }) => boolean };

const NAV_SECTIONS: NavSection[] = [
  {
    title: "Dashboard",
    items: [
      { href: "/", label: "Overview", icon: LayoutDashboard },
      { href: "/programs", label: "Programs", icon: GraduationCap },
      { href: "/recommendations", label: "Recommendations", icon: Compass },
      { href: "/job-fit", label: "Job Fit", icon: Briefcase },
    ],
  },
  {
    title: "Admin",
    items: [{ href: "/all-universities", label: "All Universities", icon: Globe }],
    show: (ctx) => ctx.canSwitchUniversity,
  },
  {
    title: "Editor",
    items: [{ href: "/my-curriculum", label: "My Curriculum", icon: PencilLine }],
    show: (ctx) => ctx.role === "org_admin",
  },
  {
    title: "About",
    items: [
      { href: "/methodology", label: "Methodology", icon: BookOpenCheck },
      { href: "/admin", label: "Data & Admin", icon: Settings },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, canSwitchUniversity, logout } = useAuth();
  const ctx = { canSwitchUniversity, role: user?.role };

  return (
    <aside className="flex h-full w-64 shrink-0 flex-col overflow-y-auto bg-primary-dark px-4 py-6 text-white">
      <div className="mb-8 flex items-center gap-2.5 px-2">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--accent)]/20 ring-1 ring-[var(--accent)]/40">
          <GraduationCap className="h-5 w-5 text-[var(--accent)]" aria-hidden />
        </span>
        <span className="font-display text-lg font-bold tracking-tight">CurriculumLens</span>
      </div>

      <nav className="flex-1 space-y-5">
        {NAV_SECTIONS.filter((s) => !s.show || s.show(ctx)).map((section) => (
          <div key={section.title}>
            <div className="mb-1.5 px-2 text-[11px] font-semibold uppercase tracking-widest text-white/45">{section.title}</div>
            <ul className="space-y-0.5">
              {section.items.map((item) => {
                const active = pathname === item.href;
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      aria-current={active ? "page" : undefined}
                      className={`flex items-center gap-2.5 rounded-md border-l-2 py-2 pl-3 pr-3 text-sm transition-colors ${
                        active
                          ? "border-[var(--accent)] bg-white/10 font-medium text-white"
                          : "border-transparent text-white/75 hover:bg-white/5 hover:text-white"
                      }`}
                    >
                      <Icon className="h-4 w-4 opacity-80" aria-hidden />
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {user && (
        <div className="mt-auto border-t border-white/10 pt-4 text-sm">
          <div className="px-2 font-medium">{user.full_name}</div>
          <div className="px-2 text-xs text-white/50">
            {user.org_name} · {user.role}
          </div>
          <button
            onClick={() => logout()}
            className="mt-3 w-full rounded-md border border-white/15 py-1.5 text-xs text-white/70 hover:bg-white/10 hover:text-white"
          >
            Log out
          </button>
        </div>
      )}
    </aside>
  );
}
