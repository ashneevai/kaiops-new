"use client";

import { WorkflowContextBanner } from "@/components/workflow-context-banner";
import { useWorkflowStore } from "@/lib/store/workflow-store";

function formatTime(value: string | null | undefined): string {
  if (!value) {
    return "—";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleTimeString();
}

export default function AuditCenterPage() {
  const workflow = useWorkflowStore((state) => state.workflow);

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">Audit Center</h2>
      <WorkflowContextBanner workflow={workflow} />

      {workflow ? (
        <article className="k-card">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left">
                <th className="px-3 py-2">Time</th>
                <th className="px-3 py-2">Actor</th>
                <th className="px-3 py-2">Action</th>
                <th className="px-3 py-2">Entity</th>
              </tr>
            </thead>
            <tbody>
              {workflow.events.map((event) => (
                <tr key={event.sequence} className="border-t border-black/5 dark:border-white/5">
                  <td className="px-3 py-2">{formatTime(workflow.generated_at)}</td>
                  <td className="px-3 py-2">{event.agent}</td>
                  <td className="px-3 py-2">{event.action}</td>
                  <td className="px-3 py-2 font-mono text-xs">{workflow.incident.id}</td>
                </tr>
              ))}
              <tr className="border-t border-black/5 dark:border-white/5">
                <td className="px-3 py-2">{formatTime(workflow.approval.decided_at)}</td>
                <td className="px-3 py-2">{workflow.approval.approver}</td>
                <td className="px-3 py-2">approval.{workflow.approval.decision.toLowerCase()}</td>
                <td className="px-3 py-2 font-mono text-xs">{workflow.incident.id}</td>
              </tr>
              <tr className="border-t border-black/5 dark:border-white/5">
                <td className="px-3 py-2">{formatTime(workflow.remediation_action.completed_at)}</td>
                <td className="px-3 py-2">kaiops.automation</td>
                <td className="px-3 py-2">automation.{workflow.remediation_action.action_type}</td>
                <td className="px-3 py-2 font-mono text-xs">{workflow.remediation_action.target}</td>
              </tr>
              <tr className="border-t border-black/5 dark:border-white/5">
                <td className="px-3 py-2">{formatTime(workflow.closure_report.validated_at)}</td>
                <td className="px-3 py-2">kaiops.closure</td>
                <td className="px-3 py-2">incident.{workflow.closure_report.health_restored ? "closed" : "open"}</td>
                <td className="px-3 py-2 font-mono text-xs">{workflow.incident.id}</td>
              </tr>
            </tbody>
          </table>
        </article>
      ) : null}
    </section>
  );
}
