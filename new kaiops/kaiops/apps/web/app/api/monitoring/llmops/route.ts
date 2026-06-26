import { NextRequest, NextResponse } from "next/server";

const apiBaseUrl = process.env.KAIOPS_API_BASE_URL ?? process.env.NEXT_PUBLIC_KAIOPS_API_BASE_URL ?? "http://localhost:8000";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const service = request.nextUrl.searchParams.get("service")?.trim();

  if (!service) {
    return NextResponse.json({ detail: "service query parameter is required" }, { status: 400 });
  }

  try {
    const url = `${apiBaseUrl}/api/v1/monitoring/llmops?service=${encodeURIComponent(service)}`;
    const response = await fetch(url, { cache: "no-store" });
    const body = await response.json();

    return NextResponse.json(body, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        found: false,
        service,
        incident_id: null,
        incident_key: null,
        total_prompt_tokens: 0,
        total_completion_tokens: 0,
        total_tokens: 0,
        total_estimated_cost_usd: 0,
        agents: [],
        note: error instanceof Error ? error.message : "Failed to load persisted LLMOps telemetry",
      },
      { status: 200 }
    );
  }
}
