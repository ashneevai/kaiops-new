export default function RCAPage() {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">RCA View</h2>
      <article className="k-card">
        <h3 className="font-semibold">Primary RCA</h3>
        <p className="mt-2 text-sm">Connection pool exhaustion caused retry storms and elevated API latency.</p>
      </article>
      <article className="k-card">
        <h3 className="font-semibold">Contributing Factors</h3>
        <ul className="mt-2 space-y-2 text-sm">
          <li>Misconfigured autoscaling floor</li>
          <li>Replica lag > 2.5s</li>
          <li>Long running migration lock contention</li>
        </ul>
      </article>
    </section>
  );
}
