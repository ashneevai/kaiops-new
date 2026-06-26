import { KPIGrid, ServiceImpactChart, type KPIItem } from "@/components/dashboard-widgets";
import { buildAlertId, getMonitoringOverview, getPrometheusAlerts } from "@/lib/monitoring";

export const dynamic = "force-dynamic";

function formatTimestamp(timestamp: string | null) {
  if (!timestamp) {
    return "Never";
  }

  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }

  return date.toLocaleString();
}

function formatDuration(seconds: number | null) {
  if (seconds === null || Number.isNaN(seconds)) {
    return "n/a";
  }

  return `${seconds.toFixed(2)}s`;
}

function statusClass(health: string) {
  return health === "up"
    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300"
    : "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300";
}

export default async function DashboardPage() {
  const monitoring = await getMonitoringOverview();
  const liveAlerts = await getPrometheusAlerts();
  const recentLiveAlerts = liveAlerts.alerts.slice(0, 5);
  const monitoringKpis: KPIItem[] = [
    { label: "Open Incidents", value: "42" },
    { label: "Critical Incidents", value: "7" },
    { label: "MTTR", value: "38m" },
    { label: "Automation Success", value: "94.2%" },
    { label: "Healthy Targets", value: `${monitoring.summary.healthy_targets}/${monitoring.summary.total_targets}` },
    {
      label: "Prometheus",
      value: monitoring.connected
        ? monitoring.summary.self_monitoring_enabled
          ? "Self-monitoring enabled"
          : "Connected"
        : "Unavailable",
    },
  ];

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">Executive Dashboard</h2>
      <KPIGrid items={monitoringKpis} />
      <div className="grid gap-4 lg:grid-cols-2">
        <ServiceImpactChart />
        <article className="k-card">
          <h3 className="text-sm font-semibold">Recent Alerts</h3>
          {recentLiveAlerts.length > 0 ? (
            <ul className="mt-3 space-y-2 text-sm">
              {recentLiveAlerts.map((alert) => (
                <li key={buildAlertId(alert)}>
                  Prometheus: {alert.service} - {alert.summary}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">
              No active Prometheus alerts right now.
            </p>
          )}
        </article>
      </div>
      <article className="k-card">
        <h3 className="text-sm font-semibold">Recent Incidents</h3>
        <ul className="mt-3 space-y-2 text-sm">
          <li>INC-12A89F2A: Investigating</li>
          <li>INC-8C2310EF: Mitigating</li>
          <li>INC-31DD940E: Resolved</li>
        </ul>
      </article>
      <section className="k-card space-y-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="text-sm font-semibold">Prometheus Monitoring</h3>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
              Live target health and scrape details from the configured Prometheus instance.
            </p>
          </div>
          <span
            className={`inline-flex w-fit rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide ${
              monitoring.connected
                ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300"
                : "bg-rose-100 text-rose-700 dark:bg-rose-500/20 dark:text-rose-300"
            }`}
          >
            {monitoring.connected ? "Connected" : "Unavailable"}
          </span>
        </div>

        <dl className="grid gap-3 text-sm md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-lg border border-black/10 p-3 dark:border-white/10">
            <dt className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Prometheus URL</dt>
            <dd className="mt-2 break-all font-medium">{monitoring.prometheus_url}</dd>
          </div>
          <div className="rounded-lg border border-black/10 p-3 dark:border-white/10">
            <dt className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Monitored Jobs</dt>
            <dd className="mt-2 font-medium">
              {monitoring.summary.monitored_jobs.length > 0 ? monitoring.summary.monitored_jobs.join(", ") : "None yet"}
            </dd>
          </div>
          <div className="rounded-lg border border-black/10 p-3 dark:border-white/10">
            <dt className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Last Refresh</dt>
            <dd className="mt-2 font-medium">{formatTimestamp(monitoring.generated_at)}</dd>
          </div>
          <div className="rounded-lg border border-black/10 p-3 dark:border-white/10">
            <dt className="text-xs uppercase tracking-wide text-slate-600 dark:text-slate-300">Self Monitoring</dt>
            <dd className="mt-2 font-medium">
              {monitoring.summary.self_monitoring_enabled ? "Enabled" : "Not detected"}
            </dd>
          </div>
        </dl>

        {monitoring.error ? (
          <p className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-200">
            Unable to load Prometheus details: {monitoring.error}
          </p>
        ) : null}

        {monitoring.targets.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-b border-black/10 text-slate-600 dark:border-white/10 dark:text-slate-300">
                  <th className="px-3 py-2 font-medium">Job</th>
                  <th className="px-3 py-2 font-medium">Endpoint</th>
                  <th className="px-3 py-2 font-medium">Health</th>
                  <th className="px-3 py-2 font-medium">Last Scrape</th>
                  <th className="px-3 py-2 font-medium">Duration</th>
                  <th className="px-3 py-2 font-medium">Last Error</th>
                </tr>
              </thead>
              <tbody>
                {monitoring.targets.map((target) => (
                  <tr key={`${target.job}-${target.endpoint}`} className="border-b border-black/5 dark:border-white/5">
                    <td className="px-3 py-2 font-medium">{target.job}</td>
                    <td className="px-3 py-2">{target.endpoint}</td>
                    <td className="px-3 py-2">
                      <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold uppercase ${statusClass(target.health)}`}>
                        {target.health}
                      </span>
                    </td>
                    <td className="px-3 py-2">{formatTimestamp(target.last_scrape)}</td>
                    <td className="px-3 py-2">{formatDuration(target.last_scrape_duration_seconds)}</td>
                    <td className="px-3 py-2">{target.last_error || "None"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Prometheus has not reported any active targets yet. Start the Docker services and refresh this page.
          </p>
        )}
      </section>
    </section>
  );
}
