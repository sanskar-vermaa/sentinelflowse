import { AppShell } from "../../components/AppShell";
import { Badge } from "../../components/Badge";

const timeline = [
  "Incident created with high severity",
  "Payments team assigned",
  "Rollback candidate identified",
  "Customer impact update posted"
];

export default function IncidentDetailPage({ params }: { params: { id: string } }) {
  return (
    <AppShell>
      <div className="toolbar">
        <div>
          <h1>{params.id}</h1>
          <p>Checkout latency above threshold</p>
        </div>
        <Badge tone="danger">high</Badge>
      </div>
      <div className="detail-grid">
        <article className="card">
          <h2>Summary</h2>
          <p>p95 latency crossed the configured threshold for the checkout service in production.</p>
          <div className="meta-row"><span>Status</span><Badge tone="warning">open</Badge></div>
          <div className="meta-row"><span>Owner</span><strong>Payments</strong></div>
        </article>
        <article className="card">
          <h2>Timeline</h2>
          <div className="stack">
            {timeline.map((item) => <div className="timeline-item" key={item}>{item}</div>)}
          </div>
        </article>
      </div>
    </AppShell>
  );
}

