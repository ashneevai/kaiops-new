import { NextResponse } from "next/server";

const apiBaseUrl =
  process.env.KAIOPS_API_BASE_URL ??
  process.env.NEXT_PUBLIC_KAIOPS_API_BASE_URL ??
  "http://localhost:8000";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await fetch(`${apiBaseUrl}/api/v1/sample/flows`, { cache: "no-store" });
    const body = await response.json();
    return NextResponse.json(body, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        flows: [],
        error: error instanceof Error ? error.message : "Sample flow catalog is unavailable",
      },
      { status: 200 },
    );
  }
}
