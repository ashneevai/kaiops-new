"use client";

import { WorkflowContextBanner } from "@/components/workflow-context-banner";
import { useWorkflowStore } from "@/lib/store/workflow-store";

export default function RCAPage() {
  const workflow = useWorkflowStore((state) => state.workflow);

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">RCA View</h2>
      <WorkflowContextBanner workflow={workflow} />

      {workflow ? (
        <>
          <article className="k-card">
            <h3 className="font-semibold">Primary RCA</h3>
            <p className="mt-2 text-sm">{workflow.recommendation.root_cause}</p>
            <p className="mt-1 text-xs text-slate-600 dark:text-slate-300">
              Confidence {Math.round(workflow.recommendation.confidence * 100)}% · Risk{" "}
              <span className="font-semibold uppercase">{workflow.recommendation.risk}</span>
            </p>
          </article>

          <article className="k-card">
            <h3 className="font-semibold">Impact</h3>
            <p className="mt-2 text-sm">{workflow.recommendation.impact}</p>
          </article>

          <article className="k-card">
            <h3 className="font-semibold">Rationale</h3>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{workflow.recommendation.rationale}</p>
          </article>

          <article className="k-card">
            <h3 className="font-semibold">Contributing Factors</h3>
            <ul className="mt-2 space-y-2 text-sm">
              {workflow.context.recent_changes.map((change) => (
                <li key={change}>Recent change: {change}</li>
              ))}
              {workflow.context.dependency_services.map((service) => (
                <li key={service}>Dependency exposure: {service}</li>
              ))}
            </ul>
          </article>
        </>
      ) : null}
    </section>
  );
}
