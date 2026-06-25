export default function AlertExplorerPage() {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">Alert Explorer</h2>
      <article className="k-card">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left">
              <th>Source</th><th>Service</th><th>Severity</th><th>Status</th><th>Correlation</th>
            </tr>
          </thead>
          <tbody>
            <tr><td>Prometheus</td><td>checkout</td><td>critical</td><td>open</td><td>grp-a1</td></tr>
            <tr><td>Datadog</td><td>billing</td><td>high</td><td>open</td><td>grp-b4</td></tr>
            <tr><td>CloudWatch</td><td>auth</td><td>warning</td><td>investigating</td><td>grp-a1</td></tr>
          </tbody>
        </table>
      </article>
    </section>
  );
}
