import { AppShell } from "../components/AppShell";
import { Badge } from "../components/Badge";

const incidents = [
  { id: "INC-1042", title: "Checkout latency above threshold", severity: "high", status: "open", owner: "Payments" },
  { id: "INC-1041", title: "CI deploy failed for web", severity: "medium", status: "acknowledged", owner: "Platform" },
  { id: "INC-1040", title: "Webhook retry spike", severity: "low", status: "mitigated", owner: "Integrations" }
];

export default function IncidentsPage() {
  return (
    <AppShell>
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
                <th>Status</th>
                <th>Owner</th>
              </tr>
            </thead>
            <tbody>
              {incidents.map((incident) => (
                <tr key={incident.id}>
                  <td>{incident.id}</td>
                  <td><a href={`/incidents/${incident.id}`}>{incident.title}</a></td>
                  <td>
                    <Badge tone={incident.severity === "high" ? "danger" : "neutral"}>{incident.severity}</Badge>
                  </td>
                  <td><Badge tone="warning">{incident.status}</Badge></td>
                  <td>{incident.owner}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>
    </AppShell>
  );
}
