"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { clearSession, getDisplayName, getOrganization, getToken } from "../lib/session";

const navItems = [
  { href: "/", label: "Overview" },
  { href: "/incidents", label: "Incidents" },
  { href: "/alerts", label: "Alerts" },
  { href: "/workflows", label: "Workflows" },
  { href: "/audit", label: "Audit" },
  { href: "/settings", label: "Settings" }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [orgName, setOrgName] = useState<string | null>(null);
  const [displayName, setDisplayName] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    setOrgName(getOrganization()?.organization_name ?? null);
    setDisplayName(getDisplayName());
    setReady(true);
  }, [router]);

  function handleLogout() {
    clearSession();
    router.replace("/login");
  }

  if (!ready) {
    return null;
  }

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
        <div className="sidebar-footer">
          <div className="hint">{orgName}</div>
          <div className="hint">{displayName}</div>
          <button type="button" className="logout-link" onClick={handleLogout}>
            Sign out
          </button>
        </div>
      </aside>
      <section className="content">{children}</section>
    </main>
  );
}
