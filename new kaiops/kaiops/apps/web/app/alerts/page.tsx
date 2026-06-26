"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { buildAlertId, type MonitoringAlert, type MonitoringAlerts, getPrometheusAlerts } from "@/lib/monitoring";

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

export default function AlertExplorerPage() {
  const [data, setData] = useState<MonitoringAlerts | null>(null);
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

  const alerts = useMemo(() => data?.alerts ?? [], [data?.alerts]);

  return (
    <section className="space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold">Alert Explorer</h2>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
            Live Prometheus alerts with 5-second streaming refresh.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs font-semibold uppercase tracking-wide">
          <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-700 dark:bg-slate-600/30 dark:text-slate-200">
            Total {data?.total_alerts ?? 0}
          </span>
          <span className="rounded-full bg-rose-100 px-3 py-1 text-rose-700 dark:bg-rose-500/20 dark:text-rose-300">
            Firing {data?.firing_alerts ?? 0}
          </span>
          <span className="rounded-full bg-amber-100 px-3 py-1 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300">
            Pending {data?.pending_alerts ?? 0}
          </span>
          <span className="rounded-full bg-slate-200 px-3 py-1 text-slate-700 dark:bg-slate-700/50 dark:text-slate-200">
            Inactive {data?.inactive_alerts ?? 0}
          </span>
        </div>
      </div>

      <article className="k-card space-y-3">
        {data?.error ? (
          <p className="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-200">
            Unable to load Prometheus alerts: {data.error}
          </p>
        ) : null}

        <p className="text-xs text-slate-600 dark:text-slate-300">
          {loading ? "Loading alerts..." : `Last refresh: ${formatTimestamp(data?.generated_at ?? null)}`}
        </p>

        {alerts.length === 0 ? (
          <p className="text-sm text-slate-600 dark:text-slate-300">
            No active alerts right now. Prometheus rules are live; alerts appear here as soon as thresholds are met.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-600 dark:text-slate-300">
                  <th className="px-2 py-2">Alert</th>
                  <th className="px-2 py-2">Service</th>
                  <th className="px-2 py-2">Severity</th>
                  <th className="px-2 py-2">State</th>
                  <th className="px-2 py-2">Active Since</th>
                  <th className="px-2 py-2">Summary</th>
                  <th className="px-2 py-2">Drill Down</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert: MonitoringAlert) => (
                  <tr key={buildAlertId(alert)} className="border-t border-black/5 dark:border-white/5">
                    <td className="px-2 py-2 font-medium">{alert.name}</td>
                    <td className="px-2 py-2">{alert.service}</td>
                    <td className="px-2 py-2">
                      <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold uppercase ${badgeClass(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td className="px-2 py-2">
                      <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold uppercase ${badgeClass(alert.state)}`}>
                        {alert.state}
                      </span>
                    </td>
                    <td className="px-2 py-2">{formatTimestamp(alert.active_at)}</td>
                    <td className="px-2 py-2">{alert.summary}</td>
                    <td className="px-2 py-2">
                      <Link
                        href={`/alerts/${buildAlertId(alert)}`}
                        className="rounded-md border border-black/10 px-2 py-1 text-xs font-semibold uppercase tracking-wide hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
                      >
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </article>
    </section>
  );
}
