export type TriageContext = {
  incidentTitle: string;
  severity: string;
  recentAlerts: string[];
  service?: string;
};

export type TriageSuggestion = {
  summary: string;
  likelyCause: string;
  recommendedActions: string[];
};

export interface TriageProvider {
  suggest(context: TriageContext): Promise<TriageSuggestion>;
}

export class DeterministicTriageProvider implements TriageProvider {
  async suggest(context: TriageContext): Promise<TriageSuggestion> {
    return {
      summary: `${context.severity.toUpperCase()} incident: ${context.incidentTitle}`,
      likelyCause: context.recentAlerts[0] ?? "Insufficient signal collected",
      recommendedActions: [
        "Check current deploys for the affected service",
        "Review recent alert fingerprints",
        "Assign an owner before running automation"
      ]
    };
  }
}

