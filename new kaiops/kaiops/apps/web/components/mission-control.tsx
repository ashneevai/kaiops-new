"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import {
  buildAlertId,
  getPrometheusAlerts,
  type MonitoringAlert,
  type MonitoringAlerts,
} from "@/lib/monitoring";
import {
  mapServiceToFlowId,
  runFlowWorkflow,
  type FlowSummary,
  type WorkflowEvent,
  type WorkflowResponse,
} from "@/lib/sample-flows";
import { useWorkflowStore } from "@/lib/store/workflow-store";

const SOURCE_TABS = [
  { id: "alerts", label: "Live Prometheus Alerts" },
  { id: "flows", label: "Demo Flow Catalog" },
] as const;

type SourceTabId = (typeof SOURCE_TABS)[number]["id"];

const RESULT_TABS = [
  { id: "summary", label: "Incident Summary" },
  { id: "approval", label: "Approval" },
  { id: "trace", label: "Agent Trace" },
  { id: "finops", label: "FinOps" },
  { id: "closure", label: "Closed Incidents" },
] as const;

type ResultTabId = (typeof RESULT_TABS)[number]["id"];

const ALERT_REFRESH_MS = 5000;

function severityClass(severity: string): string {
  switch (severity.toLowerCase()) {
    case "critical":
    case "firing":
      return "bg-rose-100 text-rose-700 dark:bg-rose-500/20 dark:text-rose-300";
    case "high":
      return "bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-300";
    case "warning":
    case "pending":
      return "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300";
    case "inactive":
      return "bg-slate-100 text-slate-700 dark:bg-slate-600/30 dark:text-slate-200";
    default:
      return "bg-slate-100 text-slate-700 dark:bg-slate-600/30 dark:text-slate-200";
  }
}

function formatPercentage(value: number): string {
  if (Number.isNaN(value)) {
    return "n/a";
  }
  return `${Math.round(value * 100)}%`;
}

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

type RunTarget =
  | { kind: "flow"; flowId: string; label: string }
  | { kind: "alert"; alert: MonitoringAlert };

export function MissionControl({ flows }: { flows: FlowSummary[] }) {
  const [sourceTab, setSourceTab] = useState<SourceTabId>("alerts");
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");
  const [search, setSearch] = useState<string>("");
  const [activeTab, setActiveTab] = useState<ResultTabId>("summary");
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState<RunTarget | null>(null);

  const [alerts, setAlerts] = useState<MonitoringAlerts | null>(null);
  const [alertsLoading, setAlertsLoading] = useState<boolean>(true);

  const setWorkflow = useWorkflowStore((state) => state.setWorkflow);
  const workflow = useWorkflowStore((state) => state.workflow);

  useEffect(() => {
    let mounted = true;
    let inFlight = false;

    const refresh = async () => {
      if (inFlight || (typeof document !== "undefined" && document.hidden)) {
        return;
      }
      inFlight = true;
      const next = await getPrometheusAlerts();
      inFlight = false;
      if (!mounted) {
        return;
      }
      setAlerts(next);
      setAlertsLoading(false);
    };

    void refresh();
    const timer = setInterval(() => {
      void refresh();
    }, ALERT_REFRESH_MS);

    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, []);

  const filteredFlows = useMemo(() => {
    const term = search.trim().toLowerCase();
    return flows.filter((flow) => {
      const matchesSeverity = severityFilter === "ALL" || flow.severity === severityFilter;
      if (!matchesSeverity) {
        return false;
      }
      if (!term) {
        return true;
      }
      return [flow.alert_id, flow.alert_name, flow.title, flow.service, flow.description]
        .map((value) => String(value ?? "").toLowerCase())
        .some((value) => value.includes(term));
    });
  }, [flows, severityFilter, search]);

  const filteredAlerts = useMemo(() => {
    const list = alerts?.alerts ?? [];
    const term = search.trim().toLowerCase();
    return list.filter((alert) => {
      const severity = alert.severity.toUpperCase();
      const matchesSeverity = severityFilter === "ALL" || severity === severityFilter;
      if (!matchesSeverity) {
        return false;
      }
      if (!term) {
        return true;
      }
      return [alert.name, alert.service, alert.summary, alert.state]
        .map((value) => String(value ?? "").toLowerCase())
        .some((value) => value.includes(term));
    });
  }, [alerts?.alerts, severityFilter, search]);

  async function runForFlow(flowId: string, label: string) {
    setRunning({ kind: "flow", flowId, label });
    setIsRunning(true);
    setError(null);
    try {
      const data = await runFlowWorkflow(flowId);
      setWorkflow(data);
      setActiveTab("summary");
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : "Unknown workflow error";
      setError(message);
    } finally {
      setIsRunning(false);
      setRunning(null);
    }
  }

  async function runForAlert(alert: MonitoringAlert) {
    const flowId = mapServiceToFlowId(alert.service);
    setRunning({ kind: "alert", alert });
    setIsRunning(true);
    setError(null);
    try {
      const data = await runFlowWorkflow(flowId);
      setWorkflow(data);
      setActiveTab("summary");
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : "Unknown workflow error";
      setError(message);
    } finally {
      setIsRunning(false);
      setRunning(null);
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
          Pick a live alert or a demo scenario, run an end-to-end agent workflow, and review the result across the linked pages.
        </p>
      </header>

      <article className="k-card space-y-3">
        <header className="flex flex-wrap items-end gap-3">
          <div className="flex-1 space-y-1">
            <h3 className="text-sm font-semibold">Flow Control</h3>
            <p className="text-xs text-slate-600 dark:text-slate-300">
              Live alert table refreshes every {ALERT_REFRESH_MS / 1000}s. Demo flows are deterministic and safe to re-run.
            </p>
          </div>
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
            <span className="text-xs uppercase tracking-wide text-slate-500">Search</span>
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="service, alert, scenario…"
              className="mt-1 w-64 rounded-md border border-black/10 bg-white px-2 py-1 text-sm dark:border-white/10 dark:bg-ink/40"
            />
          </label>
        </header>

        <nav className="flex flex-wrap gap-2 border-b border-black/10 pb-1 dark:border-white/10">
          {SOURCE_TABS.map((tab) => {
            const isActive = tab.id === sourceTab;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setSourceTab(tab.id)}
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

        {sourceTab === "alerts" ? (
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2 text-xs font-semibold uppercase tracking-wide">
              <span className="rounded-full bg-rose-100 px-3 py-1 text-rose-700 dark:bg-rose-500/20 dark:text-rose-300">
                Firing {alerts?.firing_alerts ?? 0}
              </span>
              <span className="rounded-full bg-amber-100 px-3 py-1 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300">
                Pending {alerts?.pending_alerts ?? 0}
              </span>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-700 dark:bg-slate-600/30 dark:text-slate-200">
                Total {alerts?.total_alerts ?? 0}
              </span>
              {alerts?.connected === false ? (
                <span className="rounded-full bg-rose-100 px-3 py-1 text-rose-700 dark:bg-rose-500/20 dark:text-rose-300">
                  Prometheus unreachable
                </span>
              ) : null}
              <span className="ml-auto text-[10px] text-slate-500">
                Last refresh: {formatTimestamp(alerts?.generated_at ?? null)}
              </span>
            </div>

            {alertsLoading ? (
              <p className="text-sm text-slate-600 dark:text-slate-300">Loading live alerts…</p>
            ) : filteredAlerts.length === 0 ? (
              <p className="text-sm text-slate-600 dark:text-slate-300">
                No Prometheus alerts match the current filter. Trigger an alert in Prometheus or switch to the Demo Flow Catalog.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-black/10 text-slate-600 dark:border-white/10 dark:text-slate-300">
                      <th className="px-3 py-2 font-medium">Alert</th>
                      <th className="px-3 py-2 font-medium">Service</th>
                      <th className="px-3 py-2 font-medium">Severity</th>
                      <th className="px-3 py-2 font-medium">State</th>
                      <th className="px-3 py-2 font-medium">Active Since</th>
                      <th className="px-3 py-2 font-medium">Summary</th>
                      <th className="px-3 py-2 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredAlerts.map((alert) => {
                      const isRunningRow =
                        isRunning && running?.kind === "alert" && buildAlertId(running.alert) === buildAlertId(alert);
                      return (
                        <tr key={buildAlertId(alert)} className="border-b border-black/5 dark:border-white/5">
                          <td className="px-3 py-2 font-medium">{alert.name}</td>
                          <td className="px-3 py-2">{alert.service}</td>
                          <td className="px-3 py-2">
                            <span className={`rounded-full px-2 py-1 text-xs font-semibold uppercase ${severityClass(alert.severity)}`}>
                              {alert.severity}
                            </span>
                          </td>
                          <td className="px-3 py-2">
                            <span className={`rounded-full px-2 py-1 text-xs font-semibold uppercase ${severityClass(alert.state)}`}>
                              {alert.state}
                            </span>
                          </td>
                          <td className="px-3 py-2">{formatTimestamp(alert.active_at)}</td>
                          <td className="px-3 py-2">{alert.summary}</td>
                          <td className="px-3 py-2">
                            <div className="flex flex-wrap items-center gap-2">
                              <button
                                type="button"
                                onClick={() => runForAlert(alert)}
                                disabled={isRunning}
                                className="rounded-md bg-orange-600 px-2 py-1 text-xs font-semibold text-white shadow-sm transition hover:bg-orange-500 disabled:cursor-not-allowed disabled:opacity-60"
                              >
                                {isRunningRow ? "Running…" : "Run Workflow"}
                              </button>
                              <Link
                                href={`/alerts/${buildAlertId(alert)}`}
                                className="rounded-md border border-black/10 px-2 py-1 text-xs font-semibold uppercase tracking-wide hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
                              >
                                Drill Down
                              </Link>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-b border-black/10 text-slate-600 dark:border-white/10 dark:text-slate-300">
                  <th className="px-3 py-2 font-medium">Alert ID</th>
                  <th className="px-3 py-2 font-medium">Title</th>
                  <th className="px-3 py-2 font-medium">Service</th>
                  <th className="px-3 py-2 font-medium">Severity</th>
                  <th className="px-3 py-2 font-medium">Recommended Action</th>
                  <th className="px-3 py-2 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredFlows.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-3 py-4 text-center text-sm text-slate-600 dark:text-slate-300">
                      No demo flows match your filter.
                    </td>
                  </tr>
                ) : (
                  filteredFlows.map((flow) => {
                    const isRunningRow = isRunning && running?.kind === "flow" && running.flowId === flow.id;
                    return (
                      <tr key={flow.id} className="border-b border-black/5 dark:border-white/5">
                        <td className="px-3 py-2 font-mono text-xs">{flow.alert_id}</td>
                        <td className="px-3 py-2 font-medium">{flow.title}</td>
                        <td className="px-3 py-2">{flow.service}</td>
                        <td className="px-3 py-2">
                          <span className={`rounded-full px-2 py-1 text-xs font-semibold uppercase ${severityClass(flow.severity)}`}>
                            {flow.severity}
                          </span>
                        </td>
                        <td className="px-3 py-2">{flow.recommended_action}</td>
                        <td className="px-3 py-2">
                          <button
                            type="button"
                            onClick={() => runForFlow(flow.id, flow.title)}
                            disabled={isRunning}
                            className="rounded-md bg-orange-600 px-2 py-1 text-xs font-semibold text-white shadow-sm transition hover:bg-orange-500 disabled:cursor-not-allowed disabled:opacity-60"
                          >
                            {isRunningRow ? "Running…" : "Run Workflow"}
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}

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
            <MetricCard label="Confidence" value={formatPercentage(workflow.recommendation.confidence)} />
            <MetricCard label="Health Restored" value={workflow.closure_report.health_restored ? "Yes" : "No"} />
            <MetricCard label="Agent Handoffs" value={String(workflow.metrics.agent_handoffs)} />
          </div>

          <nav className="flex flex-wrap items-center gap-2 border-b border-black/10 pb-1 dark:border-white/10">
            {RESULT_TABS.map((tab) => {
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
            <div className="ml-auto flex flex-wrap items-center gap-2 text-xs">
              <Link
                href="/incidents"
                className="rounded-md border border-black/10 px-2 py-1 font-semibold uppercase tracking-wide hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
              >
                Command Center
              </Link>
              <Link
                href="/investigation"
                className="rounded-md border border-black/10 px-2 py-1 font-semibold uppercase tracking-wide hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
              >
                Investigation
              </Link>
              <Link
                href="/rca"
                className="rounded-md border border-black/10 px-2 py-1 font-semibold uppercase tracking-wide hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
              >
                RCA
              </Link>
              <Link
                href="/automation"
                className="rounded-md border border-black/10 px-2 py-1 font-semibold uppercase tracking-wide hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
              >
                Automation
              </Link>
              <Link
                href="/workflows"
                className="rounded-md border border-black/10 px-2 py-1 font-semibold uppercase tracking-wide hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
              >
                Workflows
              </Link>
              <Link
                href="/audit"
                className="rounded-md border border-black/10 px-2 py-1 font-semibold uppercase tracking-wide hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
              >
                Audit
              </Link>
            </div>
          </nav>

          {activeTab === "summary" ? <SummaryTab workflow={workflow} /> : null}
          {activeTab === "approval" ? <ApprovalTab workflow={workflow} /> : null}
          {activeTab === "trace" ? <TraceTab workflow={workflow} /> : null}
          {activeTab === "finops" ? <FinopsTab workflow={workflow} /> : null}
          {activeTab === "closure" ? <ClosureTab workflow={workflow} /> : null}
        </>
      ) : (
        <section className="k-card text-sm text-slate-600 dark:text-slate-300">
          Pick a live alert or demo flow above and press <span className="font-semibold">Run Workflow</span> to execute an
          end-to-end agent run. The result powers the linked pages.
        </section>
      )}
    </section>
  );
}
