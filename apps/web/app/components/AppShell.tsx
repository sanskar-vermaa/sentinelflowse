const navItems = [
  { href: "/", label: "Overview" },
  { href: "/incidents", label: "Incidents" },
  { href: "/alerts", label: "Alerts" },
  { href: "/workflows", label: "Workflows" },
  { href: "/audit", label: "Audit" },
  { href: "/settings", label: "Settings" }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">SentinelFlow</div>
        <nav className="nav">
          {navItems.map((item) => (
            <a href={item.href} key={item.href}>
              {item.label}
            </a>
          ))}
        </nav>
      </aside>
      <section className="content">{children}</section>
    </main>
  );
}
