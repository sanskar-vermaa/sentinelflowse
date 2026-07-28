import { AppShell } from "../components/AppShell";
import { Badge } from "../components/Badge";

const alerts = [
  { source: "monitor", title: "Checkout latency above threshold", service: "checkout", severity: "high" },
  { source: "github", title: "Deploy failed for web", service: "web", severity: "medium" },
  { source: "ci", title: "Webhook retry spike", service: "integrations", severity: "low" }
];

export default function AlertsPage() {
  return (
    <AppShell>
      <div className="toolbar">
        <div>
          <h1>Alerts</h1>
          <p>Normalized events from monitors, CI, GitHub, and webhooks.</p>
        </div>
      </div>
      <article className="card">
        <table className="table">
          <thead>
            <tr><th>Source</th><th>Title</th><th>Service</th><th>Severity</th></tr>
          </thead>
          <tbody>
            {alerts.map((alert) => (
              <tr key={`${alert.source}-${alert.title}`}>
                <td>{alert.source}</td>
                <td>{alert.title}</td>
                <td>{alert.service}</td>
                <td><Badge tone={alert.severity === "high" ? "danger" : "neutral"}>{alert.severity}</Badge></td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>
    </AppShell>
  );
}

