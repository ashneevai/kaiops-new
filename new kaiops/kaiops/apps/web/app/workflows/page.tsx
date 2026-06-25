export default function WorkflowBuilderPage() {
  const nodes = ["Condition", "Approval", "Automation", "Notification", "Agent"];
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">Workflow Builder</h2>
      <div className="grid gap-4 lg:grid-cols-[240px_1fr]">
        <article className="k-card">
          <h3 className="font-semibold">Nodes</h3>
          <ul className="mt-2 space-y-2 text-sm">
            {nodes.map((node) => (
              <li key={node} className="rounded border border-black/10 p-2 dark:border-white/10">{node}</li>
            ))}
          </ul>
        </article>
        <article className="k-card min-h-[420px]">
          <h3 className="font-semibold">Canvas</h3>
          <p className="mt-2 text-sm">Drag and drop node execution graph is rendered here and persisted as workflow JSON definitions.</p>
        </article>
      </div>
    </section>
  );
}
