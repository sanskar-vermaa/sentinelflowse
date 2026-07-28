import { AppShell } from "../components/AppShell";

const workflows = [
  { name: "Page on critical incidents", trigger: "incident.created", status: "Enabled" },
  { name: "Create postmortem draft", trigger: "incident.resolved", status: "Enabled" },
  { name: "Notify integration owner", trigger: "alert.ingested", status: "Paused" }
];

export default function WorkflowsPage() {
  return (
    <AppShell>
      <div className="toolbar">
        <div>
          <h1>Workflows</h1>
          <p>Automate response steps with deterministic runbooks.</p>
        </div>
      </div>
      <div className="grid">
        {workflows.map((workflow) => (
          <article className="card" key={workflow.name}>
            <h2><a href={`/workflows/${encodeURIComponent(workflow.name)}`}>{workflow.name}</a></h2>
            <p>{workflow.trigger}</p>
            <strong>{workflow.status}</strong>
          </article>
        ))}
      </div>
    </AppShell>
  );
}
