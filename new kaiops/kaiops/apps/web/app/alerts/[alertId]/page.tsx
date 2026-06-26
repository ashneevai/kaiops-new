"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import {
  deriveAlertDrilldown,
  getPersistedLLMOpsTelemetry,
  matchesAlertId,
  type MonitoringAlert,
  type MonitoringAlerts,
  type PersistedLLMOpsTelemetry,
  getPrometheusAlerts,
} from "@/lib/monitoring";

const refreshIntervalMs = 5000;

function badgeClass(value: string) {
  const lowered = value.toLowerCase();

  if (lowered === "firing" || lowered === "critical") {
    return "bg-rose-100 text-rose-700 dark:bg-rose-500/20 dark:text-rose-300";
  }

  if (lowered === "pending" || lowered === "warning") {
    return "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300";
  }

  return "bg-slate-100 text-slate-700 dark:bg-slate-600/30 dark:text-slate-200";
}

function formatTimestamp(value: string | null) {
  if (!value) {
    return "Unknown";
  }

  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export default function AlertDetailsPage() {
  const params = useParams<{ alertId: string }>();
  const alertId = params.alertId;
  const [data, setData] = useState<MonitoringAlerts | null>(null);
  const [persistedTelemetry, setPersistedTelemetry] = useState<PersistedLLMOpsTelemetry | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    let inFlight = false;

    const refresh = async () => {
      if (inFlight || document.hidden) {
        return;
      }

      inFlight = true;
      const next = await getPrometheusAlerts();
      inFlight = false;

      if (!mounted) {
        return;
      }
      setData(next);
      setLoading(false);
    };

    void refresh();
    const timer = setInterval(() => {
      void refresh();
    }, refreshIntervalMs);

    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, []);

  const alert = useMemo(() => {
    if (!data) {
      return null;
    }
    return data.alerts.find((item) => matchesAlertId(item, alertId)) ?? null;
  }, [data, alertId]);

  useEffect(() => {
    let mounted = true;
    let inFlight = false;

    if (!alert) {
      setPersistedTelemetry(null);
      return () => {
        mounted = false;
      };
    }

    const refreshTelemetry = async () => {
      if (inFlight || document.hidden) {
        return;
      }

      inFlight = true;
      const telemetry = await getPersistedLLMOpsTelemetry(alert.service);
      inFlight = false;

      if (!mounted) {
        return;
      }
      setPersistedTelemetry(telemetry);
    };

    void refreshTelemetry();
    const timer = setInterval(() => {
      void refreshTelemetry();
    }, 15000);

    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, [alert]);

  if (loading) {
    return (
      <section className="space-y-3">
        <h2 className="text-2xl font-bold">Alert Drill Down</h2>
        <article className="k-card text-sm text-slate-600 dark:text-slate-300">Loading alert details...</article>
      </section>
    );
  }

  if (!alert) {
    return (
      <section className="space-y-3">
        <h2 className="text-2xl font-bold">Alert Drill Down</h2>
        <article className="k-card space-y-3 text-sm">
          <p className="text-slate-600 dark:text-slate-300">
            This alert is no longer active or no longer available in the current Prometheus alert stream.
          </p>
          <Link href="/alerts" className="inline-flex rounded-md border border-black/10 px-3 py-2 text-xs font-semibold uppercase tracking-wide hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10">
            Back to Alerts
          </Link>
        </article>
      </section>
    );
  }

  const details = deriveAlertDrilldown(alert);

  const llmModel = persistedTelemetry?.found && persistedTelemetry.agents.length > 0
    ? persistedTelemetry.agents[0].model
    : details.llmModel;
  const promptTokens = persistedTelemetry?.found ? persistedTelemetry.total_prompt_tokens : details.promptTokens;
  const completionTokens = persistedTelemetry?.found
    ? persistedTelemetry.total_completion_tokens
    : details.completionTokens;
  const totalTokens = persistedTelemetry?.found ? persistedTelemetry.total_tokens : details.totalTokens;
  const llmCostPerHourUsd = persistedTelemetry?.found
    ? Number((persistedTelemetry.total_estimated_cost_usd * 6).toFixed(4))
    : details.llmCostPerHourUsd;
  const llmCostPerDayUsd = persistedTelemetry?.found
    ? Number((llmCostPerHourUsd * 24).toFixed(4))
    : details.llmCostPerDayUsd;

  return (
    <section className="space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold">Alert Drill Down</h2>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
            Live details generated from current alert telemetry and labels.
          </p>
        </div>
        <Link href="/alerts" className="inline-flex w-fit rounded-md border border-black/10 px-3 py-2 text-xs font-semibold uppercase tracking-wide hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10">
          Back to Alerts
        </Link>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <article className="k-card lg:col-span-2 space-y-3">
          <h3 className="text-sm font-semibold">Alert Details</h3>
          <div className="grid gap-3 text-sm md:grid-cols-2">
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Alert Name</p>
              <p className="mt-1 font-medium">{alert.name}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Service</p>
              <p className="mt-1 font-medium">{alert.service}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Status</p>
              <span className={`mt-1 inline-flex rounded-full px-2 py-1 text-xs font-semibold uppercase ${badgeClass(alert.state)}`}>
                {alert.state}
              </span>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Severity</p>
              <span className={`mt-1 inline-flex rounded-full px-2 py-1 text-xs font-semibold uppercase ${badgeClass(alert.severity)}`}>
                {alert.severity}
              </span>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Active Since</p>
              <p className="mt-1 font-medium">{formatTimestamp(alert.active_at)}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Metric Value</p>
              <p className="mt-1 font-medium">{alert.value ?? "n/a"}</p>
            </div>
          </div>
          <div className="rounded-md border border-black/10 p-3 dark:border-white/10">
            <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Summary</p>
            <p className="mt-2 text-sm">{alert.summary}</p>
            {alert.description ? <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{alert.description}</p> : null}
          </div>
        </article>

        <article className="k-card space-y-3">
          <h3 className="text-sm font-semibold">Incident Summary</h3>
          <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Incident ID</p>
          <p className="text-sm font-medium">{details.incidentId}</p>
          <p className="text-sm">{details.incidentSummary}</p>
          <p className="text-sm text-slate-600 dark:text-slate-300">Blast Radius: {details.likelyBlastRadius}</p>
        </article>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <article className="k-card space-y-3">
          <h3 className="text-sm font-semibold">FinOps Impact</h3>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Dynamic estimate derived from live alert severity and metric intensity.
          </p>
          <div className="grid gap-2 text-sm md:grid-cols-2">
            <div className="rounded-md border border-black/10 p-3 dark:border-white/10">
              <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Estimated Cost / Hour</p>
              <p className="mt-2 text-lg font-semibold">${details.estimatedCostPerHourUsd.toFixed(2)}</p>
            </div>
            <div className="rounded-md border border-black/10 p-3 dark:border-white/10">
              <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Estimated Cost / Day</p>
              <p className="mt-2 text-lg font-semibold">${details.estimatedCostPerDayUsd.toFixed(2)}</p>
            </div>
          </div>

          <div className="rounded-md border border-black/10 p-3 dark:border-white/10">
            <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">LLMOps Metrics</h4>
            <p className="mt-1 text-xs text-slate-600 dark:text-slate-300">
              {persistedTelemetry?.found
                ? `Persisted usage from incident ${persistedTelemetry.incident_key ?? persistedTelemetry.incident_id}`
                : "Using fallback estimate until persisted agent telemetry is available."}
            </p>
            <div className="mt-3 grid gap-2 text-sm md:grid-cols-2">
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Model</p>
                <p className="mt-1 font-medium">{llmModel}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Token Cost / 1K</p>
                <p className="mt-1 font-medium">${details.tokenCostPer1kUsd.toFixed(4)}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Prompt Tokens</p>
                <p className="mt-1 font-medium">{promptTokens.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Completion Tokens</p>
                <p className="mt-1 font-medium">{completionTokens.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Total Tokens</p>
                <p className="mt-1 font-medium">{totalTokens.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">LLM Cost / Hour</p>
                <p className="mt-1 font-medium">${llmCostPerHourUsd.toFixed(4)}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">LLM Cost / Day</p>
                <p className="mt-1 font-medium">${llmCostPerDayUsd.toFixed(4)}</p>
              </div>
            </div>
          </div>
        </article>

        <article className="k-card space-y-3">
          <h3 className="text-sm font-semibold">Raw Labels</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-600 dark:text-slate-300">
                  <th className="px-2 py-2">Key</th>
                  <th className="px-2 py-2">Value</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(alert.labels).map(([key, value]) => (
                  <tr key={key} className="border-t border-black/5 dark:border-white/5">
                    <td className="px-2 py-2 font-medium">{key}</td>
                    <td className="px-2 py-2">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </div>

      <article className="k-card space-y-3">
        <h3 className="text-sm font-semibold">Agent Trace (Input / Output)</h3>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          Execution trace generated from this live alert context.
        </p>
        <div className="space-y-3">
          {details.trace.map((entry) => (
            <div key={entry.step} className="rounded-md border border-black/10 p-3 dark:border-white/10">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">{entry.step}</p>
              <div className="mt-2 grid gap-3 lg:grid-cols-2">
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Input</p>
                  <pre className="mt-1 overflow-x-auto rounded bg-black/5 p-2 text-xs dark:bg-white/10">{entry.input}</pre>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Output</p>
                  <pre className="mt-1 overflow-x-auto rounded bg-black/5 p-2 text-xs dark:bg-white/10">{entry.output}</pre>
                </div>
              </div>
            </div>
          ))}
        </div>
      </article>
    </section>
  );
}
