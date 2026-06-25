export default function InvestigationPage() {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">AI Investigation View</h2>
      <div className="k-card">
        <h3 className="font-semibold">Agent Execution Graph</h3>
        <pre className="mt-2 rounded bg-black/5 p-3 text-xs dark:bg-white/10">
          {"Alert -> Context -> RCA -> Impact -> Resolution -> Validation -> Approval"}
        </pre>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <article className="k-card">
          <h3 className="font-semibold">Reasoning Timeline</h3>
          <ul className="mt-2 text-sm space-y-2">
            <li>Context Agent confidence 78%</li>
            <li>RCA Agent confidence 74%</li>
            <li>Impact Agent confidence 80%</li>
            <li>Resolution Agent confidence 76%</li>
            <li>Validation Agent confidence 82%</li>
          </ul>
        </article>
        <article className="k-card">
          <h3 className="font-semibold">Retrieved Documents</h3>
          <ul className="mt-2 text-sm space-y-2">
            <li>Runbook: checkout-db-failover-v3</li>
            <li>Postmortem: incident-2026-03-18</li>
            <li>Confluence: traffic shaping strategy</li>
          </ul>
        </article>
      </div>
      <article className="k-card">
        <h3 className="font-semibold">Decision Path</h3>
        <p className="mt-2 text-sm">DB saturation + queue depth trend + pod restart anomalies led to automated mitigation recommendation.</p>
      </article>
    </section>
  );
}
