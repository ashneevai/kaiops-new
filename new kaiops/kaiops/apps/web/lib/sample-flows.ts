export type FlowSummary = {
  id: string;
  alert_id: string;
  alert_name: string;
  alert_type: string;
  title: string;
  service: string;
  severity: string;
  recommended_action: string;
  description: string;
};

export type WorkflowEvent = {
  sequence: number;
  agent: string;
  action: string;
  input: Record<string, unknown>;
  decision: string;
  output: string;
  communicates_to: string;
  metrics: Record<string, unknown>;
};

export type WorkflowResponse = {
  mode: string;
  scenario: {
    id: string;
    title: string;
    service: string;
    severity: string;
    recommended_action: string;
    source: string;
    description: string;
  };
  alert: Record<string, unknown> & {
    id: string;
    name: string;
    source: string;
    severity: string;
    service: string;
    description: string;
    correlation_id: string;
    deduplicated_count: number;
  };
  incident: Record<string, unknown> & {
    id: string;
    title: string;
    service: string;
    severity: string;
    status: string;
  };
  decision: {
    workflow: string;
    next_action: string;
    requires_approval: boolean;
    downstream_agents: string[];
  };
  context: {
    incident_id: string;
    deployment: string;
    runbook: string;
    related_incidents: string[];
    dependency_services: string[];
    recent_changes: string[];
    metrics: Record<string, string>;
  };
  recommendation: {
    id: string;
    incident_id: string;
    root_cause: string;
    confidence: number;
    impact: string;
    recommended_action: string;
    severity: string;
    rationale: string;
    risk: string;
  };
  approval: {
    id: string;
    incident_id: string;
    recommendation_id: string;
    decision: string;
    approver: string;
    channel: string;
    comment: string;
    decided_at: string;
  };
  remediation_action: {
    id: string;
    action_type: string;
    target: string;
    status: string;
    output: string;
    parameters: Record<string, unknown>;
    completed_at: string;
  };
  closure_report: {
    incident_id: string;
    health_restored: boolean;
    alerts_cleared: number;
    knowledge_base_entry: string;
    validated_at: string;
  };
  metrics: Record<string, unknown> & {
    recommendation_confidence: number;
    agent_handoffs: number;
    health_restored: boolean;
    alerts_cleared: number;
    severity: string;
    approval_required: boolean;
  };
  finops: {
    totals: {
      input_tokens: number;
      output_tokens: number;
      total_tokens: number;
      total_cost_usd: number;
      calls: number;
      failed_calls: number;
    };
    by_provider: Array<Record<string, unknown>>;
    errors: Array<Record<string, unknown>>;
    note: string;
  };
  events: WorkflowEvent[];
  next_step: string;
  trace_id: string;
  generated_at: string;
};

const apiBaseUrl = process.env.KAIOPS_API_BASE_URL ?? "http://localhost:8000";

export const NEXT_PUBLIC_API_BASE_URL =
  process.env.NEXT_PUBLIC_KAIOPS_API_BASE_URL ?? "http://localhost:8000";

export async function getFlowCatalog(): Promise<FlowSummary[]> {
  try {
    const response = await fetch(`${apiBaseUrl}/api/v1/sample/flows`, { cache: "no-store" });
    if (!response.ok) {
      return [];
    }
    const body = (await response.json()) as { flows?: FlowSummary[] };
    return Array.isArray(body.flows) ? body.flows : [];
  } catch {
    return [];
  }
}
