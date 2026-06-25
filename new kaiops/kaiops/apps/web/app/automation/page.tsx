export default function AutomationCenterPage() {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">Automation Center</h2>
      <article className="k-card">
        <h3 className="font-semibold">Execution Controls</h3>
        <div className="mt-3 flex gap-2 text-sm">
          <button className="rounded bg-slate-800 px-3 py-1 text-white">Dry Run</button>
          <button className="rounded bg-emerald-600 px-3 py-1 text-white">Execute</button>
          <button className="rounded bg-amber-600 px-3 py-1 text-white">Rollback</button>
        </div>
      </article>
      <article className="k-card">
        <h3 className="font-semibold">Recent Runs</h3>
        <ul className="mt-2 text-sm space-y-2">
          <li>Kubernetes scale rollout - success</li>
          <li>Terraform module apply - awaiting approval</li>
          <li>Ansible remediation play - dry run pass</li>
        </ul>
      </article>
    </section>
  );
}
