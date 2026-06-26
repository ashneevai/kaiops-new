export type MonitoringTarget = {
  job: string;
  endpoint: string;
  health: string;
  labels: Record<string, string>;
  last_error: string | null;
  last_scrape: string | null;
  last_scrape_duration_seconds: number | null;
  scrape_url: string | null;
};

export type MonitoringOverview = {
  connected: boolean;
  prometheus_url: string;
  generated_at: string;
  summary: {
    total_targets: number;
    healthy_targets: number;
    unhealthy_targets: number;
    monitored_jobs: string[];
    self_monitoring_enabled: boolean;
  };
  targets: MonitoringTarget[];
  error: string | null;
};

const apiBaseUrl = process.env.KAIOPS_API_BASE_URL ?? "http://localhost:8000";
const fallbackPrometheusUrl = process.env.KAIOPS_PROMETHEUS_URL ?? "http://localhost:9090";

export async function getMonitoringOverview(): Promise<MonitoringOverview> {
  try {
    const response = await fetch(`${apiBaseUrl}/api/v1/monitoring/overview`, { cache: "no-store" });

    if (!response.ok) {
      throw new Error(`Monitoring request failed with status ${response.status}`);
    }

    return (await response.json()) as MonitoringOverview;
  } catch (error) {
    return {
      connected: false,
      prometheus_url: fallbackPrometheusUrl,
      generated_at: new Date().toISOString(),
      summary: {
        total_targets: 0,
        healthy_targets: 0,
        unhealthy_targets: 0,
        monitored_jobs: [],
        self_monitoring_enabled: false,
      },
      targets: [],
      error: error instanceof Error ? error.message : "Monitoring data is unavailable",
    };
  }
}
