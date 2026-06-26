"use client";

import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis } from "recharts";

export type KPIItem = {
  label: string;
  value: string;
};

const data = [
  { name: "auth", incidents: 12 },
  { name: "checkout", incidents: 23 },
  { name: "search", incidents: 7 },
  { name: "billing", incidents: 16 },
];

const defaultKpis: KPIItem[] = [
  { label: "Open Incidents", value: "42" },
  { label: "Critical Incidents", value: "7" },
  { label: "MTTR", value: "38m" },
  { label: "Automation Success", value: "94.2%" },
  { label: "AI Confidence", value: "81%" },
  { label: "Top Services Impacted", value: "checkout, billing" },
];

export function KPIGrid({ items = defaultKpis }: { items?: KPIItem[] }) {
  return (
    <div className="grid gap-3 md:grid-cols-3">
      {items.map(({ label, value }) => (
        <article key={label} className="k-card">
          <p className="text-xs uppercase tracking-wider text-slate-600 dark:text-slate-300">{label}</p>
          <h3 className="mt-2 text-xl font-semibold">{value}</h3>
        </article>
      ))}
    </div>
  );
}

export function ServiceImpactChart() {
  return (
    <section className="k-card h-72">
      <h3 className="mb-3 text-sm font-semibold">Top Services Impacted</h3>
      <ResponsiveContainer width="100%" height="90%">
        <BarChart data={data}>
          <XAxis dataKey="name" />
          <YAxis />
          <Bar dataKey="incidents" fill="#d34e24" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </section>
  );
}
