export default function KnowledgeHubPage() {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">Knowledge Hub</h2>
      <article className="k-card">
        <h3 className="font-semibold">Semantic Search</h3>
        <input className="mt-3 w-full rounded border p-2 text-sm" placeholder="Search runbooks, incidents, confluence, github..." />
      </article>
      <article className="k-card">
        <h3 className="font-semibold">Top Results</h3>
        <ul className="mt-2 space-y-2 text-sm">
          <li>Runbook: checkout-db-failover-v3 (source: runbooks)</li>
          <li>Incident: INC-91AF22C (source: historical incidents)</li>
          <li>Confluence: database saturation response (source: confluence)</li>
        </ul>
      </article>
    </section>
  );
}
