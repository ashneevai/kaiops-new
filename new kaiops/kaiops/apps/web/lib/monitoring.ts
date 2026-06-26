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

export type MonitoringAlert = {
  name: string;
  state: string;
  severity: string;
  service: string;
  summary: string;
  description: string | null;
  active_at: string | null;
  value: string | null;
  source_url: string | null;
  labels: Record<string, string>;
  annotations: Record<string, string>;
};

export type MonitoringAlerts = {
  connected: boolean;
  prometheus_url: string;
  generated_at: string;
  total_alerts: number;
  firing_alerts: number;
  pending_alerts: number;
  inactive_alerts: number;
  alerts: MonitoringAlert[];
  error: string | null;
};

export type AlertDrilldown = {
  incidentId: string;
  incidentSummary: string;
  estimatedCostPerHourUsd: number;
  estimatedCostPerDayUsd: number;
  llmModel: string;
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  tokenCostPer1kUsd: number;
  llmCostPerHourUsd: number;
  llmCostPerDayUsd: number;
  likelyBlastRadius: string;
  trace: Array<{ step: string; input: string; output: string }>;
};

export type PersistedLLMOpsTelemetry = {
  found: boolean;
  service: string;
  incident_id: string | null;
  incident_key: string | null;
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_tokens: number;
  total_estimated_cost_usd: number;
  agents: Array<{
    agent_name: string;
    model: string;
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    estimated_cost_usd: number;
  }>;
  note: string | null;
};

const apiBaseUrl =
  process.env.KAIOPS_API_BASE_URL ?? process.env.NEXT_PUBLIC_KAIOPS_API_BASE_URL ?? "http://localhost:8000";
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

export async function getPrometheusAlerts(): Promise<MonitoringAlerts> {
  const endpoint = typeof window === "undefined" ? `${apiBaseUrl}/api/v1/monitoring/alerts` : "/api/monitoring/alerts";

  try {
    const response = await fetch(endpoint, { cache: "no-store" });

    if (!response.ok) {
      throw new Error(`Monitoring alerts request failed with status ${response.status}`);
    }

    return (await response.json()) as MonitoringAlerts;
  } catch (error) {
    return {
      connected: false,
      prometheus_url: fallbackPrometheusUrl,
      generated_at: new Date().toISOString(),
      total_alerts: 0,
      firing_alerts: 0,
      pending_alerts: 0,
      inactive_alerts: 0,
      alerts: [],
      error: error instanceof Error ? error.message : "Monitoring alerts are unavailable",
    };
  }
}

export function buildAlertId(alert: MonitoringAlert): string {
  return encodeURIComponent(`${alert.name}::${alert.service}`);
}

export function matchesAlertId(alert: MonitoringAlert, alertId: string): boolean {
  return buildAlertId(alert) === alertId;
}

function toNumber(value: string | null): number {
  if (!value) {
    return 0;
  }
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function shortHash(input: string): string {
  let hash = 0;
  for (let i = 0; i < input.length; i += 1) {
    hash = (hash * 31 + input.charCodeAt(i)) >>> 0;
  }
  return hash.toString(16).toUpperCase().padStart(8, "0").slice(0, 8);
}

export function deriveAlertDrilldown(alert: MonitoringAlert): AlertDrilldown {
  const metricValue = Math.max(toNumber(alert.value), 0.0001);
  const severityMultiplier = alert.severity.toLowerCase() === "critical" ? 80 : alert.severity.toLowerCase() === "warning" ? 35 : 15;
  const costPerHour = Number((metricValue * severityMultiplier * 12).toFixed(2));
  const costPerDay = Number((costPerHour * 24).toFixed(2));
  const incidentId = `INC-${shortHash(buildAlertId(alert))}`;

  const llmModel = "gpt-4o-mini";
  const tokenCostPer1kUsd = 0.0008;
  const promptTokens = Math.max(Math.round(metricValue * 6500), 900);
  const completionTokens = Math.max(Math.round(promptTokens * 0.35), 320);
  const totalTokens = promptTokens + completionTokens;
  const llmCostPerHour = Number(((totalTokens / 1000) * tokenCostPer1kUsd * 6).toFixed(4));
  const llmCostPerDay = Number((llmCostPerHour * 24).toFixed(4));

  const likelyBlastRadius =
    alert.service.includes("api") || alert.service.includes("checkout")
      ? "Customer-facing latency and conversion impact"
      : alert.service.includes("prometheus")
      ? "Reduced observability confidence across teams"
      : "Internal service degradation with downstream risk";

  return {
    incidentId,
    incidentSummary: `${alert.name} is ${alert.state} for ${alert.service}. ${alert.summary}`,
    estimatedCostPerHourUsd: costPerHour,
    estimatedCostPerDayUsd: costPerDay,
    llmModel,
    promptTokens,
    completionTokens,
    totalTokens,
    tokenCostPer1kUsd,
    llmCostPerHourUsd: llmCostPerHour,
    llmCostPerDayUsd: llmCostPerDay,
    likelyBlastRadius,
    trace: [
      {
        step: "ingest_alert_context",
        input: JSON.stringify(
          {
            alertname: alert.name,
            service: alert.service,
            severity: alert.severity,
            state: alert.state,
            value: alert.value,
          },
          null,
          2
        ),
        output: `Context normalized for ${alert.service} with severity ${alert.severity}.`,
      },
      {
        step: "correlate_incident",
        input: JSON.stringify(
          {
            labels: alert.labels,
            annotations: alert.annotations,
          },
          null,
          2
        ),
        output: `Correlated to incident ${incidentId} with status ${alert.state}.`,
      },
      {
        step: "recommend_actions",
        input: JSON.stringify(
          {
            metricValue,
            blastRadius: likelyBlastRadius,
          },
          null,
          2
        ),
        output: "Recommend scale adjustment, traffic shaping, and runbook execution with approval gate.",
      },
    ],
  };
}

export async function getPersistedLLMOpsTelemetry(service: string): Promise<PersistedLLMOpsTelemetry | null> {
  const endpoint =
    typeof window === "undefined"
      ? `${apiBaseUrl}/api/v1/monitoring/llmops?service=${encodeURIComponent(service)}`
      : `/api/monitoring/llmops?service=${encodeURIComponent(service)}`;

  try {
    const response = await fetch(endpoint, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`LLMOps telemetry request failed with status ${response.status}`);
    }
    return (await response.json()) as PersistedLLMOpsTelemetry;
  } catch {
    return null;
  }
}
