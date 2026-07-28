import { AppShell } from "../components/AppShell";

const logs = [
  { action: "incident.created", target: "INC-1042", actor: "Demo Admin" },
  { action: "incident.updated", target: "INC-1041", actor: "Platform Lead" },
  { action: "workflow.created", target: "Page on critical incidents", actor: "Demo Admin" }
];

export default function AuditPage() {
  return (
    <AppShell>
      <div className="toolbar">
        <div>
          <h1>Audit log</h1>
          <p>Trace important organization actions and response decisions.</p>
        </div>
      </div>
      <article className="card">
        <table className="table">
          <thead>
            <tr><th>Action</th><th>Target</th><th>Actor</th></tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={`${log.action}-${log.target}`}>
                <td>{log.action}</td>
                <td>{log.target}</td>
                <td>{log.actor}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>
    </AppShell>
  );
}

