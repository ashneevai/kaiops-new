"use client";

import { WorkflowContextBanner } from "@/components/workflow-context-banner";
import { useWorkflowStore } from "@/lib/store/workflow-store";

export default function InvestigationPage() {
  const workflow = useWorkflowStore((state) => state.workflow);

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">AI Investigation View</h2>
      <WorkflowContextBanner workflow={workflow} />

      {workflow ? (
        <>
          <div className="k-card">
            <h3 className="font-semibold">Agent Execution Graph</h3>
            <pre className="mt-2 overflow-x-auto rounded bg-black/5 p-3 text-xs dark:bg-white/10">
              {workflow.events.map((event) => `Step ${event.sequence}: ${event.agent}`).join(" -> ")}
            </pre>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <article className="k-card">
              <h3 className="font-semibold">Reasoning Timeline</h3>
              <ul className="mt-2 space-y-2 text-sm">
                {workflow.events.map((event) => (
                  <li key={event.sequence}>
                    <span className="font-semibold">{event.agent}:</span> {event.decision}
                  </li>
                ))}
              </ul>
            </article>
            <article className="k-card">
              <h3 className="font-semibold">Retrieved Context</h3>
              <ul className="mt-2 space-y-2 text-sm">
                <li>
                  <span className="font-semibold">Runbook:</span> {workflow.context.runbook}
                </li>
                {workflow.context.related_incidents.map((incident) => (
                  <li key={incident}>
                    <span className="font-semibold">Related incident:</span> {incident}
                  </li>
                ))}
                {workflow.context.recent_changes.map((change) => (
                  <li key={change}>
                    <span className="font-semibold">Recent change:</span> {change}
                  </li>
                ))}
              </ul>
            </article>
          </div>

          <article className="k-card">
            <h3 className="font-semibold">Decision Path</h3>
            <p className="mt-2 text-sm">
              {workflow.context.metrics.saturation} saturation, trend {workflow.context.metrics.trend}, with{" "}
              {workflow.context.dependency_services.length} dependency services led the Resolution Intelligence Agent to recommend{" "}
              <span className="font-semibold">{workflow.recommendation.recommended_action}</span>.
            </p>
          </article>
        </>
      ) : null}
    </section>
  );
}
