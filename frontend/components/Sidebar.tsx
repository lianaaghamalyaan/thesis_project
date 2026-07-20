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
    <aside className="flex h-full w-60 shrink-0 flex-col bg-primary-dark px-4 py-5 text-white">
      <div className="mb-6 flex items-center gap-2 text-lg font-bold">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/15">
          <GraduationCap className="h-5 w-5" aria-hidden />
        </span>
        CurriculumLens
      </div>

      <nav className="flex-1 space-y-5">
        {NAV_SECTIONS.filter((s) => !s.show || s.show(ctx)).map((section) => (
          <div key={section.title}>
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-white/60">{section.title}</div>
            <ul className="space-y-0.5">
              {section.items.map((item) => {
                const active = pathname === item.href;
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      aria-current={active ? "page" : undefined}
                      className={`flex items-center gap-2.5 rounded-lg px-3 py-1.5 text-sm ${
                        active ? "bg-white/15 font-medium" : "hover:bg-white/10"
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
