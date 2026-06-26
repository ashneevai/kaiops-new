"use client";

import { useMemo, useState } from "react";

import {
  type FlowSummary,
  type WorkflowEvent,
  type WorkflowResponse,
} from "@/lib/sample-flows";

const TABS = [
  { id: "summary", label: "Incident Summary" },
  { id: "approval", label: "Approval" },
  { id: "trace", label: "Agent Trace" },
  { id: "finops", label: "FinOps" },
  { id: "closure", label: "Closed Incidents" },
] as const;

type TabId = (typeof TABS)[number]["id"];

function severityClass(severity: string): string {
  switch (severity.toUpperCase()) {
    case "CRITICAL":
      return "bg-rose-100 text-rose-700 dark:bg-rose-500/20 dark:text-rose-300";
    case "HIGH":
      return "bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-300";
    case "WARNING":
      return "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300";
    default:
      return "bg-slate-100 text-slate-700 dark:bg-slate-500/20 dark:text-slate-300";
  }
}

function formatPercentage(value: number): string {
  if (Number.isNaN(value)) {
    return "n/a";
  }
  return `${Math.round(value * 100)}%`;
}

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

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <article className="rounded-lg border border-black/10 p-3 dark:border-white/10">
      <p className="text-xs uppercase tracking-wider text-slate-600 dark:text-slate-300">{label}</p>
      <h3 className="mt-1 text-lg font-semibold">{value}</h3>
    </article>
  );
}

function TraceEvent({ event }: { event: WorkflowEvent }) {
  return (
    <li className="rounded-lg border border-black/10 p-3 text-sm dark:border-white/10">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="font-semibold">
          Step {event.sequence}: {event.agent}
        </span>
        <span className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
          handoff → {event.communicates_to}
        </span>
      </div>
      <p className="mt-2">{event.action}</p>
      <p className="mt-1 text-slate-600 dark:text-slate-300">
        <span className="font-medium">Decision:</span> {event.decision}
      </p>
      <p className="mt-1 text-slate-600 dark:text-slate-300">
        <span className="font-medium">Output:</span> {event.output}
      </p>
      <dl className="mt-2 grid grid-cols-2 gap-2 text-xs text-slate-600 dark:text-slate-300 md:grid-cols-4">
        {Object.entries(event.metrics).map(([key, value]) => (
          <div key={key} className="rounded-md bg-black/5 px-2 py-1 dark:bg-white/10">
            <dt className="font-medium uppercase tracking-wide">{key.replace(/_/g, " ")}</dt>
            <dd>{String(value)}</dd>
          </div>
        ))}
      </dl>
    </li>
  );
}

function SummaryTab({ workflow }: { workflow: WorkflowResponse }) {
  const { scenario, alert, incident, recommendation, metrics } = workflow;
  return (
    <div className="grid gap-3 md:grid-cols-2">
      <article className="k-card space-y-2">
        <h3 className="text-sm font-semibold">Scenario</h3>
        <p className="text-sm text-slate-600 dark:text-slate-300">{scenario.description}</p>
        <dl className="text-sm">
          <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
            <dt>Service</dt>
            <dd className="font-medium">{scenario.service}</dd>
          </div>
          <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
            <dt>Source</dt>
            <dd className="font-medium">{scenario.source}</dd>
          </div>
          <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
            <dt>Severity</dt>
            <dd>
              <span className={`rounded-full px-2 py-1 text-xs font-semibold uppercase ${severityClass(scenario.severity)}`}>
                {scenario.severity}
              </span>
            </dd>
          </div>
          <div className="flex justify-between py-1">
            <dt>Recommended action</dt>
            <dd className="font-medium">{scenario.recommended_action}</dd>
          </div>
        </dl>
      </article>
      <article className="k-card space-y-2">
        <h3 className="text-sm font-semibold">Recommendation</h3>
        <p className="text-sm text-slate-600 dark:text-slate-300">{recommendation.rationale}</p>
        <dl className="text-sm">
          <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
            <dt>Root cause</dt>
            <dd className="font-medium">{recommendation.root_cause}</dd>
          </div>
          <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
            <dt>Impact</dt>
            <dd className="font-medium">{recommendation.impact}</dd>
          </div>
          <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
            <dt>Confidence</dt>
            <dd className="font-medium">{formatPercentage(recommendation.confidence)}</dd>
          </div>
          <div className="flex justify-between py-1">
            <dt>Risk</dt>
            <dd className="font-medium uppercase">{recommendation.risk}</dd>
          </div>
        </dl>
      </article>
      <article className="k-card space-y-2 md:col-span-2">
        <h3 className="text-sm font-semibold">Alert & Incident</h3>
        <div className="grid gap-3 md:grid-cols-2">
          <dl className="text-sm">
            <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
              <dt>Alert ID</dt>
              <dd className="font-mono">{String(alert.id)}</dd>
            </div>
            <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
              <dt>Alert source</dt>
              <dd>{String(alert.source)}</dd>
            </div>
            <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
              <dt>Correlation ID</dt>
              <dd className="font-mono">{String(alert.correlation_id)}</dd>
            </div>
            <div className="flex justify-between py-1">
              <dt>Deduplicated count</dt>
              <dd>{String(alert.deduplicated_count)}</dd>
            </div>
          </dl>
          <dl className="text-sm">
            <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
              <dt>Incident ID</dt>
              <dd className="font-mono">{incident.id}</dd>
            </div>
            <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
              <dt>Status</dt>
              <dd className="font-medium uppercase">{incident.status}</dd>
            </div>
            <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
              <dt>Agent handoffs</dt>
              <dd>{String(metrics.agent_handoffs)}</dd>
            </div>
            <div className="flex justify-between py-1">
              <dt>Alerts cleared</dt>
              <dd>{String(metrics.alerts_cleared)}</dd>
            </div>
          </dl>
        </div>
      </article>
    </div>
  );
}

function ApprovalTab({ workflow }: { workflow: WorkflowResponse }) {
  const { approval, decision } = workflow;
  return (
    <article className="k-card space-y-3">
      <header className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold">Human Approval Layer</h3>
        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold uppercase ${
            approval.decision === "APPROVED"
              ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300"
              : "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300"
          }`}
        >
          {approval.decision}
        </span>
      </header>
      <p className="text-sm text-slate-600 dark:text-slate-300">{approval.comment}</p>
      <dl className="grid gap-3 text-sm md:grid-cols-2">
        <div className="rounded-md border border-black/10 p-3 dark:border-white/10">
          <dt className="text-xs uppercase tracking-wide text-slate-500">Approver</dt>
          <dd className="mt-1 font-medium">{approval.approver}</dd>
        </div>
        <div className="rounded-md border border-black/10 p-3 dark:border-white/10">
          <dt className="text-xs uppercase tracking-wide text-slate-500">Channel</dt>
          <dd className="mt-1 font-medium">{approval.channel}</dd>
        </div>
        <div className="rounded-md border border-black/10 p-3 dark:border-white/10">
          <dt className="text-xs uppercase tracking-wide text-slate-500">Decision time</dt>
          <dd className="mt-1 font-medium">{formatTimestamp(approval.decided_at)}</dd>
        </div>
        <div className="rounded-md border border-black/10 p-3 dark:border-white/10">
          <dt className="text-xs uppercase tracking-wide text-slate-500">Workflow</dt>
          <dd className="mt-1 font-medium">{decision.workflow}</dd>
        </div>
      </dl>
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Downstream agents</h4>
        <ul className="mt-2 flex flex-wrap gap-2 text-xs">
          {decision.downstream_agents.map((agent) => (
            <li key={agent} className="rounded-full bg-black/5 px-2 py-1 dark:bg-white/10">
              {agent}
            </li>
          ))}
        </ul>
      </div>
    </article>
  );
}

function TraceTab({ workflow }: { workflow: WorkflowResponse }) {
  return (
    <article className="k-card space-y-3">
      <header>
        <h3 className="text-sm font-semibold">Agent Handoff Trace</h3>
        <p className="text-xs text-slate-600 dark:text-slate-300">
          Trace ID <span className="font-mono">{workflow.trace_id}</span>
        </p>
      </header>
      <ul className="space-y-2">
        {workflow.events.map((event) => (
          <TraceEvent key={event.sequence} event={event} />
        ))}
      </ul>
    </article>
  );
}

function FinopsTab({ workflow }: { workflow: WorkflowResponse }) {
  const { finops } = workflow;
  return (
    <article className="k-card space-y-3">
      <header>
        <h3 className="text-sm font-semibold">FinOps Summary</h3>
        <p className="text-xs text-slate-600 dark:text-slate-300">{finops.note}</p>
      </header>
      <div className="grid gap-3 md:grid-cols-3">
        <MetricCard label="Total tokens" value={String(finops.totals.total_tokens)} />
        <MetricCard label="Total cost (USD)" value={finops.totals.total_cost_usd.toFixed(4)} />
        <MetricCard label="Calls" value={String(finops.totals.calls)} />
        <MetricCard label="Failed calls" value={String(finops.totals.failed_calls)} />
        <MetricCard label="Input tokens" value={String(finops.totals.input_tokens)} />
        <MetricCard label="Output tokens" value={String(finops.totals.output_tokens)} />
      </div>
    </article>
  );
}

function ClosureTab({ workflow }: { workflow: WorkflowResponse }) {
  const { closure_report: closure, remediation_action: remediation } = workflow;
  return (
    <article className="k-card space-y-3">
      <header className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Closure Report</h3>
        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold uppercase ${
            closure.health_restored
              ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300"
              : "bg-rose-100 text-rose-700 dark:bg-rose-500/20 dark:text-rose-300"
          }`}
        >
          {closure.health_restored ? "Health restored" : "Health not restored"}
        </span>
      </header>
      <p className="text-sm text-slate-600 dark:text-slate-300">{closure.knowledge_base_entry}</p>
      <div className="grid gap-3 md:grid-cols-2">
        <dl className="text-sm">
          <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
            <dt>Alerts cleared</dt>
            <dd>{closure.alerts_cleared}</dd>
          </div>
          <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
            <dt>Remediation action</dt>
            <dd className="font-medium">{remediation.action_type}</dd>
          </div>
          <div className="flex justify-between border-b border-black/5 py-1 dark:border-white/10">
            <dt>Remediation target</dt>
            <dd className="font-medium">{remediation.target}</dd>
          </div>
          <div className="flex justify-between py-1">
            <dt>Validated at</dt>
            <dd>{formatTimestamp(closure.validated_at)}</dd>
          </div>
        </dl>
        <article className="rounded-lg border border-black/10 p-3 text-sm dark:border-white/10">
          <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Remediation output</h4>
          <p className="mt-2 text-slate-600 dark:text-slate-300">{remediation.output}</p>
        </article>
      </div>
    </article>
  );
}

export function MissionControl({ flows }: { flows: FlowSummary[] }) {
  const [selectedFlowId, setSelectedFlowId] = useState<string>(flows[0]?.id ?? "");
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");
  const [workflow, setWorkflow] = useState<WorkflowResponse | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>("summary");
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const filteredFlows = useMemo(() => {
    if (severityFilter === "ALL") {
      return flows;
    }
    return flows.filter((flow) => flow.severity === severityFilter);
  }, [flows, severityFilter]);

  const selectedFlow = useMemo(
    () => flows.find((flow) => flow.id === selectedFlowId) ?? null,
    [flows, selectedFlowId],
  );

  async function runWorkflow() {
    if (!selectedFlowId) {
      return;
    }

    setIsRunning(true);
    setError(null);

    try {
      const response = await fetch(`/api/sample/${selectedFlowId}/workflow`, {
        method: "POST",
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error(`Workflow request failed with status ${response.status}`);
      }

      const data = (await response.json()) as WorkflowResponse;
      setWorkflow(data);
      setActiveTab("summary");
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : "Unknown workflow error";
      setError(message);
    } finally {
      setIsRunning(false);
    }
  }

  if (flows.length === 0) {
    return (
      <section className="k-card space-y-2">
        <h2 className="text-lg font-semibold">Mission Control unavailable</h2>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          The backend API is not reachable. Start the KaiOps API and reload this page to load the demo flow catalog.
        </p>
      </section>
    );
  }

  return (
    <section className="space-y-4">
      <header className="space-y-1">
        <h2 className="text-2xl font-bold">Mission Control</h2>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          Trigger an end-to-end agent workflow and explore the recommended remediation, approval, agent trace, FinOps, and closure
          report.
        </p>
      </header>

      <article className="k-card space-y-3">
        <h3 className="text-sm font-semibold">Flow Control</h3>
        <div className="grid gap-3 md:grid-cols-[180px_1fr_auto]">
          <label className="block text-sm">
            <span className="text-xs uppercase tracking-wide text-slate-500">Severity</span>
            <select
              className="mt-1 w-full rounded-md border border-black/10 bg-white px-2 py-1 text-sm dark:border-white/10 dark:bg-ink/40"
              value={severityFilter}
              onChange={(event) => setSeverityFilter(event.target.value)}
            >
              <option value="ALL">All</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="WARNING">Warning</option>
            </select>
          </label>
          <label className="block text-sm">
            <span className="text-xs uppercase tracking-wide text-slate-500">Flow</span>
            <select
              className="mt-1 w-full rounded-md border border-black/10 bg-white px-2 py-1 text-sm dark:border-white/10 dark:bg-ink/40"
              value={selectedFlowId}
              onChange={(event) => setSelectedFlowId(event.target.value)}
            >
              {filteredFlows.map((flow) => (
                <option key={flow.id} value={flow.id}>
                  {flow.alert_id} · {flow.title} · {flow.service} · {flow.severity}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            onClick={runWorkflow}
            disabled={isRunning || !selectedFlowId}
            className="self-end rounded-md bg-orange-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-orange-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isRunning ? "Running…" : "Run Selected Flow"}
          </button>
        </div>
        {selectedFlow ? (
          <p className="text-xs text-slate-600 dark:text-slate-300">
            <span className="font-medium uppercase">{selectedFlow.severity}</span> · {selectedFlow.alert_name} ·{" "}
            {selectedFlow.description}
          </p>
        ) : null}
        {error ? (
          <p className="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-200">
            {error}
          </p>
        ) : null}
      </article>

      {workflow ? (
        <>
          <div className="grid gap-3 md:grid-cols-4">
            <MetricCard label="Severity" value={workflow.scenario.severity} />
            <MetricCard
              label="Confidence"
              value={formatPercentage(workflow.recommendation.confidence)}
            />
            <MetricCard
              label="Health Restored"
              value={workflow.closure_report.health_restored ? "Yes" : "No"}
            />
            <MetricCard label="Agent Handoffs" value={String(workflow.metrics.agent_handoffs)} />
          </div>

          <nav className="flex flex-wrap gap-2 border-b border-black/10 pb-1 dark:border-white/10">
            {TABS.map((tab) => {
              const isActive = tab.id === activeTab;
              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id)}
                  className={`rounded-t-md px-3 py-1 text-sm font-medium transition ${
                    isActive
                      ? "bg-black/5 text-slate-900 dark:bg-white/10 dark:text-white"
                      : "text-slate-600 hover:bg-black/5 dark:text-slate-300 dark:hover:bg-white/10"
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </nav>

          {activeTab === "summary" ? <SummaryTab workflow={workflow} /> : null}
          {activeTab === "approval" ? <ApprovalTab workflow={workflow} /> : null}
          {activeTab === "trace" ? <TraceTab workflow={workflow} /> : null}
          {activeTab === "finops" ? <FinopsTab workflow={workflow} /> : null}
          {activeTab === "closure" ? <ClosureTab workflow={workflow} /> : null}
        </>
      ) : (
        <section className="k-card text-sm text-slate-600 dark:text-slate-300">
          Select a flow and press <span className="font-semibold">Run Selected Flow</span> to execute an end-to-end demo workflow.
        </section>
      )}
    </section>
  );
}
