import { KPIGrid, ServiceImpactChart } from "@/components/dashboard-widgets";

export default function DashboardPage() {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">Executive Dashboard</h2>
      <KPIGrid />
      <div className="grid gap-4 lg:grid-cols-2">
        <ServiceImpactChart />
        <article className="k-card">
          <h3 className="text-sm font-semibold">Recent Alerts</h3>
          <ul className="mt-3 space-y-2 text-sm">
            <li>Datadog: checkout latency above SLO</li>
            <li>Prometheus: db CPU saturation</li>
            <li>CloudWatch: lambda error rate spike</li>
          </ul>
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
    </section>
  );
}
