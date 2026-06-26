import { NextRequest, NextResponse } from "next/server";

const apiBaseUrl =
  process.env.KAIOPS_API_BASE_URL ??
  process.env.NEXT_PUBLIC_KAIOPS_API_BASE_URL ??
  "http://localhost:8000";

export const dynamic = "force-dynamic";

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ flowId: string }> },
) {
  const { flowId } = await context.params;

  if (!flowId?.trim()) {
    return NextResponse.json({ detail: "flowId is required" }, { status: 400 });
  }

  try {
    const response = await fetch(`${apiBaseUrl}/api/v1/sample/${encodeURIComponent(flowId)}/workflow`, {
      method: "POST",
      cache: "no-store",
      headers: {
        "x-trace-id": request.headers.get("x-trace-id") ?? "",
      },
    });

    const body = await response.json();
    return NextResponse.json(body, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        detail:
          error instanceof Error
            ? error.message
            : "Failed to run selected sample workflow",
      },
      { status: 502 },
    );
  }
}
