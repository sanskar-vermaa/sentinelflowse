import { AppShell } from "./components/AppShell";

export default function NotFound() {
  return (
    <AppShell>
      <article className="card">
        <h1>Page not found</h1>
        <p>The requested operations view does not exist.</p>
        <a className="button-link" href="/">Back to overview</a>
      </article>
    </AppShell>
  );
}

