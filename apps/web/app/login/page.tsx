export default function LoginPage() {
  return (
    <main className="auth-page">
      <section className="auth-panel">
        <div>
          <h1>SentinelFlow</h1>
          <p>Sign in to triage incidents, review alerts, and manage response workflows.</p>
        </div>
        <form className="form">
          <label>
            Email
            <input type="email" placeholder="ops@example.com" />
          </label>
          <label>
            Password
            <input type="password" placeholder="••••••••••" />
          </label>
          <button type="button">Sign in</button>
        </form>
        <p className="hint">Demo: admin@sentinelflow.dev / sentinelflow-demo</p>
      </section>
    </main>
  );
}
