"use client";

import { WorkflowContextBanner } from "@/components/workflow-context-banner";
import { useWorkflowStore } from "@/lib/store/workflow-store";

export default function KnowledgeHubPage() {
  const workflow = useWorkflowStore((state) => state.workflow);

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">Knowledge Hub</h2>
      <WorkflowContextBanner workflow={workflow} />

      <article className="k-card">
        <h3 className="font-semibold">Semantic Search</h3>
        <input
          className="mt-3 w-full rounded border p-2 text-sm"
          placeholder="Search runbooks, incidents, confluence, github..."
        />
      </article>

      {workflow ? (
        <article className="k-card space-y-2">
          <h3 className="font-semibold">Context Linked to {workflow.incident.id}</h3>
          <ul className="mt-2 space-y-2 text-sm">
            <li>
              <span className="font-semibold">Runbook:</span> {workflow.context.runbook}
            </li>
            {workflow.context.related_incidents.map((item) => (
              <li key={item}>
                <span className="font-semibold">Related incident:</span> {item}
              </li>
            ))}
            {workflow.context.recent_changes.map((change) => (
              <li key={change}>
                <span className="font-semibold">Change record:</span> {change}
              </li>
            ))}
            {workflow.context.dependency_services.map((service) => (
              <li key={service}>
                <span className="font-semibold">Dependency:</span> {service}
              </li>
            ))}
          </ul>
        </article>
      ) : null}
    </section>
  );
}
