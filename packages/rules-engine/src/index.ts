export type AlertSignal = {
  source: string;
  title: string;
  service?: string;
  environment?: string;
  labels?: string[];
  payload: Record<string, unknown>;
};

export type Severity = "low" | "medium" | "high" | "critical";

const criticalTerms = ["outage", "data loss", "payment failed", "security breach"];
const highTerms = ["latency", "error rate", "deploy failed", "retry storm"];

export function calculateSeverity(alert: AlertSignal): Severity {
  const text = `${alert.title} ${(alert.labels ?? []).join(" ")}`.toLowerCase();

  if (criticalTerms.some((term) => text.includes(term))) {
    return "critical";
  }

  if (highTerms.some((term) => text.includes(term))) {
    return "high";
  }

  if (alert.environment === "production") {
    return "medium";
  }

  return "low";
}

export function buildDedupeKey(alert: AlertSignal): string {
  const service = alert.service ?? "unknown-service";
  const environment = alert.environment ?? "unknown-env";
  const normalizedTitle = alert.title.trim().toLowerCase().replace(/\s+/g, "-");
  return `${alert.source}:${service}:${environment}:${normalizedTitle}`;
}

