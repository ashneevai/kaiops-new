"use client";

import Link from "next/link";

import type { WorkflowResponse } from "@/lib/sample-flows";

export function WorkflowContextBanner({ workflow }: { workflow: WorkflowResponse | null }) {
  if (!workflow) {
    return (
      <article className="k-card flex flex-col gap-2 border border-amber-200 bg-amber-50 text-sm dark:border-amber-500/30 dark:bg-amber-500/10">
        <p>
          No active workflow yet. Go to{" "}
          <Link href="/mission-control" className="font-semibold underline">
            Mission Control
          </Link>{" "}
          and run a flow or click a Prometheus alert.
        </p>
      </article>
    );
  }

  return (
    <article className="k-card flex flex-wrap items-center gap-3 text-xs">
      <span className="rounded-full bg-emerald-100 px-3 py-1 font-semibold uppercase tracking-wide text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300">
        Workflow active
      </span>
      <span className="font-mono">{workflow.incident.id}</span>
      <span>{workflow.scenario.title}</span>
      <span className="ml-auto">
        <Link href="/mission-control" className="font-semibold uppercase underline">
          Back to Mission Control
        </Link>
      </span>
    </article>
  );
}
