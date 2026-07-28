import { AppShell } from "./components/AppShell";

const stats = [
  { label: "Open incidents", value: "18" },
  { label: "Alerts processed", value: "1,284" },
  { label: "Automation runs", value: "342" },
  { label: "Mean time to ack", value: "7m" }
];

const queue = [
  "Checkout latency above threshold",
  "Webhook retry spike",
  "Deploy failed for web"
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
        <div className="grid grid-four">
          {stats.map((item) => (
            <article className="card" key={item.label}>
              <div className="stat">{item.label}</div>
              <div className="value">{item.value}</div>
            </article>
          ))}
        </div>
        <article className="card section-card">
          <h2>Response queue</h2>
          <div className="stack">
            {queue.map((item) => (
              <div className="queue-row" key={item}>
                <span>{item}</span>
                <a href="/incidents">Review</a>
              </div>
            ))}
          </div>
        </article>
    </AppShell>
  );
}
