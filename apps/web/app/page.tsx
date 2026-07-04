const stats = [
  { label: "Open incidents", value: "18" },
  { label: "Alerts processed", value: "1,284" },
  { label: "Automation runs", value: "342" }
];

export default function DashboardPage() {
  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">SentinelFlow</div>
        <nav className="nav">
          <a href="/">Overview</a>
          <a href="/incidents">Incidents</a>
          <a href="/workflows">Workflows</a>
          <a href="/settings">Settings</a>
        </nav>
      </aside>
      <section className="content">
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
      </section>
    </main>
  );
}

