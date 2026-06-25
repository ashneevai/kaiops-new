export default function AuditCenterPage() {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">Audit Center</h2>
      <article className="k-card">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left"><th>Time</th><th>Actor</th><th>Action</th><th>Entity</th></tr>
          </thead>
          <tbody>
            <tr><td>09:20</td><td>ops.admin</td><td>approval.granted</td><td>incident INC-12A89F2A</td></tr>
            <tr><td>09:21</td><td>kaiops.agent</td><td>automation.executed</td><td>runbook RB-343</td></tr>
            <tr><td>09:25</td><td>ops.lead</td><td>incident.closed</td><td>INC-12A89F2A</td></tr>
          </tbody>
        </table>
      </article>
    </section>
  );
}
