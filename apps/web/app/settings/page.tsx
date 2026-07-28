import { AppShell } from "../components/AppShell";

const keys = [
  { name: "Production ingest", prefix: "sf_prod_8a2", status: "Active" },
  { name: "CI alerts", prefix: "sf_ci_91b4", status: "Active" }
];

export default function SettingsPage() {
  return (
    <AppShell>
      <div className="toolbar">
        <div>
          <h1>Settings</h1>
          <p>Manage API keys and organization controls.</p>
        </div>
      </div>
      <article className="card">
        <h2>API keys</h2>
        <form className="inline-form">
          <input placeholder="New key name" />
          <button type="button">Create key</button>
        </form>
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Prefix</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {keys.map((key) => (
              <tr key={key.prefix}>
                <td>{key.name}</td>
                <td>{key.prefix}</td>
                <td>{key.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>
    </AppShell>
  );
}
