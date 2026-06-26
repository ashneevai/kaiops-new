"use client";

import { WorkflowContextBanner } from "@/components/workflow-context-banner";
import { useWorkflowStore } from "@/lib/store/workflow-store";

function formatTimestamp(value: string | null | undefined): string {
  if (!value) {
    return "—";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

export default function AutomationCenterPage() {
  const workflow = useWorkflowStore((state) => state.workflow);
  const history = useWorkflowStore((state) => state.history);

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">Automation Center</h2>
      <WorkflowContextBanner workflow={workflow} />

      {workflow ? (
        <article className="k-card space-y-3">
          <header className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="font-semibold">Current Remediation</h3>
            <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300">
              {workflow.remediation_action.status}
            </span>
          </header>
          <p className="text-sm">{workflow.remediation_action.output}</p>
          <dl className="grid gap-3 text-sm md:grid-cols-2">
            <div className="rounded-md border border-black/10 p-3 dark:border-white/10">
              <dt className="text-xs uppercase tracking-wide text-slate-500">Action type</dt>
              <dd className="mt-1 font-medium">{workflow.remediation_action.action_type}</dd>
            </div>
            <div className="rounded-md border border-black/10 p-3 dark:border-white/10">
              <dt className="text-xs uppercase tracking-wide text-slate-500">Target</dt>
              <dd className="mt-1 font-medium">{workflow.remediation_action.target}</dd>
            </div>
            <div className="rounded-md border border-black/10 p-3 dark:border-white/10">
              <dt className="text-xs uppercase tracking-wide text-slate-500">Completed at</dt>
              <dd className="mt-1 font-medium">{formatTimestamp(workflow.remediation_action.completed_at)}</dd>
            </div>
            <div className="rounded-md border border-black/10 p-3 dark:border-white/10">
              <dt className="text-xs uppercase tracking-wide text-slate-500">Approval ID</dt>
              <dd className="mt-1 font-mono text-xs">{workflow.approval.id}</dd>
            </div>
          </dl>
          <div className="flex gap-2 text-sm">
            <button className="rounded bg-slate-800 px-3 py-1 text-white" disabled>
              Dry Run
            </button>
            <button className="rounded bg-emerald-600 px-3 py-1 text-white" disabled>
              Execute
            </button>
            <button className="rounded bg-amber-600 px-3 py-1 text-white" disabled>
              Rollback
            </button>
          </div>
        </article>
      ) : null}

      {history.length > 0 ? (
        <article className="k-card space-y-2">
          <h3 className="font-semibold">Recent Automation Runs</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-b border-black/10 text-slate-600 dark:border-white/10 dark:text-slate-300">
                  <th className="px-3 py-2 font-medium">Incident</th>
                  <th className="px-3 py-2 font-medium">Action</th>
                  <th className="px-3 py-2 font-medium">Target</th>
                  <th className="px-3 py-2 font-medium">Status</th>
                  <th className="px-3 py-2 font-medium">Completed</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={item.trace_id} className="border-b border-black/5 dark:border-white/5">
                    <td className="px-3 py-2 font-mono text-xs">{item.incident.id}</td>
                    <td className="px-3 py-2">{item.remediation_action.action_type}</td>
                    <td className="px-3 py-2">{item.remediation_action.target}</td>
                    <td className="px-3 py-2 uppercase">{item.remediation_action.status}</td>
                    <td className="px-3 py-2">{formatTimestamp(item.remediation_action.completed_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      ) : null}
    </section>
  );
}
