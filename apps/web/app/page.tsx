import { AppShell } from "./components/AppShell";

const stats = [
  { label: "Open incidents", value: "18" },
  { label: "Alerts processed", value: "1,284" },
  { label: "Automation runs", value: "342" }
];

export default function DashboardPage() {
  return (
    <AppShell>
        <div className="toolbar">
          <div>
            <h1>Operations overview</h1>
            <p>Monitor incidents, alert flow, and automation health.</p>
          </div>
        </div>
        <div className="grid">
          {stats.map((item) => (
            <article className="card" key={item.label}>
              <div className="stat">{item.label}</div>
              <div className="value">{item.value}</div>
            </article>
          ))}
        </div>
    </AppShell>
  );
}
