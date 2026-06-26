import { NextResponse } from "next/server";

const apiBaseUrl = process.env.KAIOPS_API_BASE_URL ?? process.env.NEXT_PUBLIC_KAIOPS_API_BASE_URL ?? "http://localhost:8000";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await fetch(`${apiBaseUrl}/api/v1/monitoring/alerts`, { cache: "no-store" });
    const body = await response.json();

    return NextResponse.json(body, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        connected: false,
        prometheus_url: process.env.KAIOPS_PROMETHEUS_URL ?? "http://localhost:9090",
        generated_at: new Date().toISOString(),
        total_alerts: 0,
        firing_alerts: 0,
        pending_alerts: 0,
        alerts: [],
        error: error instanceof Error ? error.message : "Monitoring alerts are unavailable",
      },
      { status: 200 }
    );
  }
}
