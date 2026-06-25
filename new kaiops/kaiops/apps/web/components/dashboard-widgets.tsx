"use client";

import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis } from "recharts";

const data = [
  { name: "auth", incidents: 12 },
  { name: "checkout", incidents: 23 },
  { name: "search", incidents: 7 },
  { name: "billing", incidents: 16 },
];

export function KPIGrid() {
  const kpis = [
    ["Open Incidents", "42"],
    ["Critical Incidents", "7"],
    ["MTTR", "38m"],
    ["Automation Success", "94.2%"],
    ["AI Confidence", "81%"],
    ["Top Services Impacted", "checkout, billing"],
  ];

  return (
    <div className="grid gap-3 md:grid-cols-3">
      {kpis.map(([label, value]) => (
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
