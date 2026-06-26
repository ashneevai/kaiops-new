"use client";

import Link from "next/link";
import { useEffect } from "react";

import { useUIStore } from "@/lib/store/ui-store";

const nav = [
  ["Dashboard", "/dashboard"],
  ["Mission Control", "/mission-control"],
  ["Alerts", "/alerts"],
  ["Knowledge", "/knowledge"],
  ["Admin", "/admin"],
] as const;

export function AppLayout({ children }: { children: React.ReactNode }) {
  const { dark, toggleDark } = useUIStore();

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [dark]);

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 border-b border-black/10 bg-white/80 backdrop-blur dark:border-white/10 dark:bg-ink/80">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
          <div>
            <h1 className="text-lg font-semibold tracking-wide">KaiOps</h1>
            <p className="text-xs text-slate-600 dark:text-slate-300">Autonomous Operations Platform</p>
          </div>
          <button onClick={toggleDark} className="rounded-md border px-3 py-1 text-sm">
            {dark ? "Light" : "Dark"}
          </button>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-4 p-4 md:grid-cols-[220px_1fr]">
        <aside className="k-card h-fit">
          <nav className="space-y-2">
            {nav.map(([label, href]) => (
              <Link key={href} href={href} className="block rounded-md px-2 py-1 text-sm hover:bg-black/5 dark:hover:bg-white/10">
                {label}
              </Link>
            ))}
          </nav>
        </aside>
        <main className="space-y-4 animate-rise">{children}</main>
      </div>
    </div>
  );
}
