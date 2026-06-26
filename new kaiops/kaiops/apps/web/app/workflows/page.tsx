"use client";

import { WorkflowContextBanner } from "@/components/workflow-context-banner";
import { useWorkflowStore } from "@/lib/store/workflow-store";

export default function WorkflowBuilderPage() {
  const workflow = useWorkflowStore((state) => state.workflow);

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">Workflow Builder</h2>
      <WorkflowContextBanner workflow={workflow} />

      {workflow ? (
        <article className="k-card space-y-3">
          <header className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="font-semibold">Executed Path</h3>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-700 dark:bg-slate-600/30 dark:text-slate-200">
              {workflow.decision.workflow}
            </span>
          </header>
          <p className="text-sm">
            Next action: <span className="font-semibold">{workflow.decision.next_action}</span>
          </p>
          <ol className="space-y-2 text-sm">
            {workflow.events.map((event) => (
              <li key={event.sequence} className="rounded-md border border-black/10 p-3 dark:border-white/10">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-semibold">
                    Step {event.sequence}: {event.agent}
                  </span>
                  <span className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
                    → {event.communicates_to}
                  </span>
                </div>
                <p className="mt-1 text-slate-600 dark:text-slate-300">{event.action}</p>
                <p className="mt-1 text-xs text-slate-500">{event.decision}</p>
              </li>
            ))}
          </ol>
        </article>
      ) : null}
    </section>
  );
}
