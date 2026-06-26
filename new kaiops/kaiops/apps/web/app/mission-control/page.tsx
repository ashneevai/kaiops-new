import { MissionControl } from "@/components/mission-control";
import { getFlowCatalog } from "@/lib/sample-flows";

export const dynamic = "force-dynamic";

export default async function MissionControlPage() {
  const flows = await getFlowCatalog();
  return <MissionControl flows={flows} />;
}
