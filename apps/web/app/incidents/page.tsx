const incidents = [
  { id: "INC-1042", title: "Checkout latency above threshold", severity: "high", owner: "Payments" },
  { id: "INC-1041", title: "CI deploy failed for web", severity: "medium", owner: "Platform" },
  { id: "INC-1040", title: "Webhook retry spike", severity: "low", owner: "Integrations" }
];

export default function IncidentsPage() {
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
          <h1>Incidents</h1>
        </div>
        <article className="card">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Severity</th>
                <th>Owner</th>
              </tr>
            </thead>
            <tbody>
              {incidents.map((incident) => (
                <tr key={incident.id}>
                  <td>{incident.id}</td>
                  <td>{incident.title}</td>
                  <td className={incident.severity === "high" ? "severity-high" : undefined}>{incident.severity}</td>
                  <td>{incident.owner}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>
      </section>
    </main>
  );
}

