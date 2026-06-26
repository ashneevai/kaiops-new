"use client";

import { WorkflowContextBanner } from "@/components/workflow-context-banner";
import { useWorkflowStore } from "@/lib/store/workflow-store";

function formatTimestamp(value: string | undefined | null): string {
  if (!value) {
    return "—";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

export default function IncidentCommandCenterPage() {
  const workflow = useWorkflowStore((state) => state.workflow);
  const history = useWorkflowStore((state) => state.history);

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">Incident Command Center</h2>
      <WorkflowContextBanner workflow={workflow} />

      {workflow ? (
        <>
          <div className="grid gap-4 lg:grid-cols-3">
            <article className="k-card lg:col-span-2 space-y-2">
              <h3 className="font-semibold">Incident Summary</h3>
              <p className="text-sm">
                <span className="font-mono">{workflow.incident.id}</span> · {workflow.scenario.title} · Status:{" "}
                <span className="font-semibold uppercase">{workflow.incident.status}</span>
              </p>
              <p className="text-sm text-slate-600 dark:text-slate-300">{workflow.scenario.description}</p>
              <dl className="grid gap-2 text-sm md:grid-cols-2">
                <div className="rounded-md border border-black/10 p-2 dark:border-white/10">
                  <dt className="text-xs uppercase tracking-wide text-slate-500">Service</dt>
                  <dd className="mt-1 font-medium">{workflow.scenario.service}</dd>
                </div>
                <div className="rounded-md border border-black/10 p-2 dark:border-white/10">
                  <dt className="text-xs uppercase tracking-wide text-slate-500">Severity</dt>
                  <dd className="mt-1 font-medium uppercase">{workflow.scenario.severity}</dd>
                </div>
                <div className="rounded-md border border-black/10 p-2 dark:border-white/10">
                  <dt className="text-xs uppercase tracking-wide text-slate-500">Source</dt>
                  <dd className="mt-1 font-medium">{workflow.scenario.source}</dd>
                </div>
                <div className="rounded-md border border-black/10 p-2 dark:border-white/10">
                  <dt className="text-xs uppercase tracking-wide text-slate-500">Confidence</dt>
                  <dd className="mt-1 font-medium">{Math.round(workflow.recommendation.confidence * 100)}%</dd>
                </div>
              </dl>
            </article>
            <article className="k-card space-y-2">
              <h3 className="font-semibold">Approval Actions</h3>
              <p className="text-sm">
                <span className="font-semibold uppercase text-emerald-700 dark:text-emerald-300">
                  {workflow.approval.decision}
                </span>{" "}
                by {workflow.approval.approver}
              </p>
              <p className="text-xs text-slate-600 dark:text-slate-300">{workflow.approval.comment}</p>
              <div className="mt-2 flex gap-2">
                <button className="rounded bg-emerald-600 px-3 py-1 text-white" disabled>
                  Approve
                </button>
                <button className="rounded bg-rose-600 px-3 py-1 text-white" disabled>
                  Reject
                </button>
              </div>
            </article>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <article className="k-card">
              <h3 className="font-semibold">Timeline</h3>
              <ul className="mt-2 space-y-2 text-sm">
                {workflow.events.map((event) => (
                  <li key={event.sequence} className="flex items-start gap-2">
                    <span className="font-mono text-xs text-slate-500">Step {event.sequence}</span>
                    <span>
                      <span className="font-semibold">{event.agent}</span> — {event.action}
                    </span>
                  </li>
                ))}
              </ul>
            </article>
            <article className="k-card">
              <h3 className="font-semibold">AI Findings</h3>
              <p className="mt-2 text-sm">
                Confidence {Math.round(workflow.recommendation.confidence * 100)}%. Main risk:{" "}
                <span className="font-medium">{workflow.recommendation.risk}</span>.
              </p>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{workflow.recommendation.rationale}</p>
            </article>
          </div>

          <div className="grid gap-4 lg:grid-cols-3">
            <article className="k-card">
              <h3 className="font-semibold">Root Cause</h3>
              <p className="text-sm mt-2">{workflow.recommendation.root_cause}</p>
            </article>
            <article className="k-card">
              <h3 className="font-semibold">Impact Analysis</h3>
              <p className="text-sm mt-2">{workflow.recommendation.impact}</p>
            </article>
            <article className="k-card">
              <h3 className="font-semibold">Automation Actions</h3>
              <ul className="text-sm mt-2 space-y-1">
                <li>
                  <span className="font-medium">{workflow.remediation_action.action_type}</span> on{" "}
                  {workflow.remediation_action.target}
                </li>
                <li>Status: {workflow.remediation_action.status}</li>
                <li>Completed: {formatTimestamp(workflow.remediation_action.completed_at)}</li>
              </ul>
            </article>
          </div>
        </>
      ) : null}

      {history.length > 0 ? (
        <article className="k-card space-y-2">
          <h3 className="font-semibold">Recent Runs</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-b border-black/10 text-slate-600 dark:border-white/10 dark:text-slate-300">
                  <th className="px-3 py-2 font-medium">Incident</th>
                  <th className="px-3 py-2 font-medium">Scenario</th>
                  <th className="px-3 py-2 font-medium">Severity</th>
                  <th className="px-3 py-2 font-medium">Health</th>
                  <th className="px-3 py-2 font-medium">Generated</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={item.trace_id} className="border-b border-black/5 dark:border-white/5">
                    <td className="px-3 py-2 font-mono text-xs">{item.incident.id}</td>
                    <td className="px-3 py-2">{item.scenario.title}</td>
                    <td className="px-3 py-2 uppercase">{item.scenario.severity}</td>
                    <td className="px-3 py-2">{item.closure_report.health_restored ? "Restored" : "Not restored"}</td>
                    <td className="px-3 py-2">{formatTimestamp(item.generated_at)}</td>
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
