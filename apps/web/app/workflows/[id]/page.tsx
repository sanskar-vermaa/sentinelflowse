import { AppShell } from "../../components/AppShell";
import { Badge } from "../../components/Badge";

const steps = ["Notify on-call", "Create timeline note", "Open postmortem draft"];

export default function WorkflowDetailPage({ params }: { params: { id: string } }) {
  return (
    <AppShell>
      <div className="toolbar">
        <div>
          <h1>{params.id}</h1>
          <p>Automation runbook details and planned execution steps.</p>
        </div>
        <Badge tone="success">enabled</Badge>
      </div>
      <article className="card">
        <h2>Steps</h2>
        <div className="stack">
          {steps.map((step, index) => (
            <div className="queue-row" key={step}>
              <span>{index + 1}. {step}</span>
              <Badge>queued</Badge>
            </div>
          ))}
        </div>
      </article>
    </AppShell>
  );
}

